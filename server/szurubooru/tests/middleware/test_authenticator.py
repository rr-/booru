from unittest.mock import patch

from szurubooru.func import auth, users, user_tokens
from szurubooru.middleware import authenticator
from szurubooru.rest import errors
import pytest


def test_process_request_no_header(context_factory):
    ctx = context_factory()
    authenticator.process_request(ctx)
    assert ctx.user.name is None


def test_process_request_basic_auth_valid(context_factory, user_factory):
    user = user_factory()
    ctx = context_factory(headers={
        'Authorization': "Basic dGVzdFVzZXI6dGVzdFBhc3N3b3Jk"
    })
    with patch('szurubooru.func.auth.is_valid_password'), \
            patch('szurubooru.func.users.get_user_by_name'):
        users.get_user_by_name.return_value = user
        auth.is_valid_password.return_value = True
        authenticator.process_request(ctx)
        assert ctx.user == user


def test_process_request_token_auth_valid(context_factory, user_token_factory):
    user_token = user_token_factory()
    ctx = context_factory(headers={
        'Authorization': "Token dGVzdFVzZXI6dGVzdFRva2Vu"
    })
    with patch('szurubooru.func.auth.is_valid_token'), \
            patch('szurubooru.func.users.get_user_by_name'), \
            patch('szurubooru.func.user_tokens.get_user_token_by_user_and_token'):
        users.get_user_by_name.return_value = user_token.user
        user_tokens.get_user_token_by_user_and_token.return_value = user_token
        auth.is_valid_password.return_value = True
        authenticator.process_request(ctx)
        assert ctx.user == user_token.user


def test_process_request_bad_header(context_factory):
    ctx = context_factory(headers={
        'Authorization': "Secret SuperSecretValue"
    })
    with pytest.raises(errors.HttpBadRequest):
        authenticator.process_request(ctx)
