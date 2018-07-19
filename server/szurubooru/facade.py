import os
import time
import logging
import threading
from typing import Callable, Any, Type

import coloredlogs
import sqlalchemy as sa
import sqlalchemy.orm.exc
from szurubooru import config, db, errors, rest
from szurubooru.func import posts, file_uploads
# pylint: disable=unused-import
from szurubooru import api, middleware


def _map_error(
        ex: Exception,
        target_class: Type[rest.errors.BaseHttpError],
        title: str) -> rest.errors.BaseHttpError:
    return target_class(
        name=type(ex).__name__,
        title=title,
        description=str(ex),
        extra_fields=getattr(ex, 'extra_fields', {}))


def _on_auth_error(ex: Exception) -> None:
    raise _map_error(ex, rest.errors.HttpForbidden, 'Authentication error')


def _on_validation_error(ex: Exception) -> None:
    raise _map_error(ex, rest.errors.HttpBadRequest, 'Validation error')


def _on_search_error(ex: Exception) -> None:
    raise _map_error(ex, rest.errors.HttpBadRequest, 'Search error')


def _on_integrity_error(ex: Exception) -> None:
    raise _map_error(ex, rest.errors.HttpConflict, 'Integrity violation')


def _on_not_found_error(ex: Exception) -> None:
    raise _map_error(ex, rest.errors.HttpNotFound, 'Not found')


def _on_processing_error(ex: Exception) -> None:
    raise _map_error(ex, rest.errors.HttpBadRequest, 'Processing error')


def _on_third_party_error(ex: Exception) -> None:
    raise _map_error(
        ex,
        rest.errors.HttpInternalServerError,
        'Server configuration error')


def _on_stale_data_error(_ex: Exception) -> None:
    raise rest.errors.HttpConflict(
        name='IntegrityError',
        title='Integrity violation',
        description=(
            'Someone else modified this in the meantime. '
            'Please try again.'))


def validate_config() -> None:
    '''
    Check whether config doesn't contain errors that might prove
    lethal at runtime.
    '''
    from szurubooru.func.auth import RANK_MAP
    for privilege, rank in config.config['privileges'].items():
        if rank not in RANK_MAP.values():
            raise errors.ConfigError(
                'Rank %r for privilege %r is missing' % (rank, privilege))
    if config.config['default_rank'] not in RANK_MAP.values():
        raise errors.ConfigError(
            'Default rank %r is not on the list of known ranks' % (
                config.config['default_rank']))

    for key in ['data_url', 'data_dir']:
        if not config.config[key]:
            raise errors.ConfigError(
                'Service is not configured: %r is missing' % key)

    if not os.path.isabs(config.config['data_dir']):
        raise errors.ConfigError(
            'data_dir must be an absolute path')

    if not config.config['database']:
        raise errors.ConfigError('Database is not configured')


def purge_old_uploads() -> None:
    while True:
        try:
            file_uploads.purge_old_uploads()
        except Exception as ex:
            logging.exception(ex)
        time.sleep(60 * 5)


def create_app() -> Callable[[Any, Any], Any]:
    ''' Create a WSGI compatible App object. '''
    validate_config()
    coloredlogs.install(fmt='[%(asctime)-15s] %(name)s %(message)s')
    logging.getLogger('elasticsearch').disabled = True
    if config.config['debug']:
        logging.getLogger('szurubooru').setLevel(logging.INFO)
    if config.config['show_sql']:
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    purge_thread = threading.Thread(target=purge_old_uploads)
    purge_thread.daemon = True
    purge_thread.start()

    try:
        posts.populate_reverse_search()
        db.session.commit()
    except errors.ThirdPartyError:
        pass

    rest.errors.handle(errors.AuthError, _on_auth_error)
    rest.errors.handle(errors.ValidationError, _on_validation_error)
    rest.errors.handle(errors.SearchError, _on_search_error)
    rest.errors.handle(errors.IntegrityError, _on_integrity_error)
    rest.errors.handle(errors.NotFoundError, _on_not_found_error)
    rest.errors.handle(errors.ProcessingError, _on_processing_error)
    rest.errors.handle(errors.ThirdPartyError, _on_third_party_error)
    rest.errors.handle(sa.orm.exc.StaleDataError, _on_stale_data_error)

    return rest.application


app = create_app()  # pylint: disable=invalid-name
