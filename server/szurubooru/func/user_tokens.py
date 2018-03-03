import pytz
from dateutil import parser as dateutil_parser
from datetime import datetime
from typing import Any, Optional, List, Dict, Callable
from szurubooru import db, model, rest, errors
from szurubooru.func import auth, serialization, users, util


class InvalidEnabledError(errors.ValidationError):
    pass


class InvalidExpirationError(errors.ValidationError):
    pass


class InvalidNoteError(errors.ValidationError):
    pass


class UserTokenSerializer(serialization.BaseSerializer):
    def __init__(
            self,
            user_token: model.UserToken,
            auth_user: model.User) -> None:
        self.user_token = user_token
        self.auth_user = auth_user

    def _serializers(self) -> Dict[str, Callable[[], Any]]:
        return {
            'user': self.serialize_user,
            'token': self.serialize_token,
            'note': self.serialize_note,
            'enabled': self.serialize_enabled,
            'expirationTime': self.serialize_expiration_time,
            'creationTime': self.serialize_creation_time,
            'lastEditTime': self.serialize_last_edit_time,
            'version': self.serialize_version,
        }

    def serialize_user(self) -> Any:
        return users.serialize_micro_user(self.user_token.user, self.auth_user)

    def serialize_creation_time(self) -> Any:
        return self.user_token.creation_time

    def serialize_last_edit_time(self) -> Any:
        return self.user_token.last_edit_time

    def serialize_token(self) -> Any:
        return self.user_token.token

    def serialize_note(self) -> Any:
        return self.user_token.note

    def serialize_enabled(self) -> Any:
        return self.user_token.enabled

    def serialize_expiration_time(self) -> Any:
        return self.user_token.expiration_time

    def serialize_version(self) -> Any:
        return self.user_token.version


def serialize_user_token(
        user_token: Optional[model.UserToken],
        auth_user: model.User,
        options: List[str] = []) -> Optional[rest.Response]:
    if not user_token:
        return None
    return UserTokenSerializer(user_token, auth_user).serialize(options)


def get_by_user_and_token(
        user: model.User, token: str) -> model.UserToken:
    return (db.session.query(model.UserToken)
            .filter(model.UserToken.user_id == user.user_id,
                    model.UserToken.token == token)
            .one_or_none())


def get_user_tokens(user: model.User) -> List[model.UserToken]:
    assert user
    return (db.session.query(model.UserToken)
            .filter(model.UserToken.user_id == user.user_id)
            .all())


def create_user_token(user: model.User, enabled: bool) -> model.UserToken:
    assert user
    user_token = model.UserToken()
    user_token.user = user
    user_token.token = auth.generate_authorization_token()
    user_token.enabled = enabled
    user_token.creation_time = datetime.utcnow()
    return user_token


def update_user_token_enabled(
        user_token: model.UserToken, enabled: bool) -> None:
    assert user_token
    if enabled is None:
        raise InvalidEnabledError('Enabled cannot be empty.')
    user_token.enabled = enabled


def update_user_token_edit_time(user_token: model.UserToken) -> None:
    assert user_token
    user_token.last_edit_time = datetime.utcnow()


def update_user_token_expiration_time(
        user_token: model.UserToken, expiration_time: str) -> None:
    assert user_token
    if expiration_time is not None:
        try:
            expiration_time = dateutil_parser.parse(expiration_time)
        except ValueError:
            raise InvalidExpirationError(
                'Expiration is in invalid format {}'.format(expiration_time))
        if expiration_time.tzinfo is None:
            raise InvalidExpirationError(
                'Expiration cannot be missing timezone')
        else:
            expiration_time = expiration_time.astimezone(pytz.UTC)
        if expiration_time < datetime.utcnow().replace(tzinfo=pytz.UTC):
            raise InvalidExpirationError(
                'Expiration cannot happen in the past')
    user_token.expiration_time = expiration_time


def update_user_token_note(user_token: model.UserToken, note: str) -> None:
    assert user_token
    note = note.strip() if note is not None else ''
    if util.value_exceeds_column_size(note, model.UserToken.note):
        raise InvalidNoteError('Note is too long.')
    user_token.note = note
