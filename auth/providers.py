from datetime import datetime, timedelta
import logging
import os
import urllib

from flask import g, json
from flask_ask import session
from flask_oauthlib.provider import OAuth2Provider

from models import AlexaUser, Client, Grant, Token

logger = logging.getLogger('flask_ask')

def default_provider(app):
    oauth = OAuth2Provider(app)

    @app.before_request
    def load_current_user():
        # TODO: Find a better way to get userID
        user_id = session.user.userId if session else os.getenv('ASK_AUTH_USER_ID')
        g.user = next(AlexaUser.query(user_id))

    @oauth.clientgetter
    def get_client(client_id):
        logger.debug('get client - client_id: {}\n'.format(client_id))
        return next(Client.query(client_id))

    @oauth.grantgetter
    def get_grant(client_id, code):
        logger.debug('get grant - client_id: {} code: {}\n'.format(client_id, code))
        return next(Grant.query(client_id, code))

    @oauth.tokengetter
    def get_token(access_token=None, refresh_token=None):
        if access_token:
            logger.debug('get token - access_token: {}\n'.format(access_token))
            return next(Token.query(access_token=access_token))
        if refresh_token:
            return next(Token.query(refresh_token=refresh_token))
        return None

    @oauth.grantsetter
    def set_grant(client_id, code, request, *args, **kwargs):
        expires = datetime.utcnow() + timedelta(seconds=120000)
        redirect_params = {'code': code['code'], 'state': request.state}
        logger.debug('set grant - redirect_params: {}\n'.format(json.dumps(redirect_params)))
        redirect_uri = '{}?{}'.format(request.redirect_uri, urllib.urlencode(redirect_params))
        grant = Grant(
            client_id=client_id,
            code=code['code'],
            redirect_uri=redirect_uri,
            scope=' '.join(request.scopes),
            userId=g.user.userId,
            expires=expires,
        )
        logger.debug('grant', grant.__dict__)
        grant.save()
        return grant

    @oauth.tokensetter
    def set_token(token, request, *args, **kwargs):
        logger.debug('set token - user: {}\n'.format(request.user.userId))
        tok = Token(**token)
        tok.userId = request.user.userId
        tok.client_id = request.client.client_id
        tok.save()
        return tok

    return oauth
