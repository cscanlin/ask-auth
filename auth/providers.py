from datetime import datetime, timedelta
import urllib

from flask import g
from flask_ask import session
from flask_oauthlib.provider import OAuth2Provider

from models import AlexaUser, Client, Grant, Token

def default_provider(app):
    oauth = OAuth2Provider(app)

    @app.before_request
    def load_current_user():
        g.user = next(AlexaUser.query(session.user.userId))

    @oauth.clientgetter
    def get_client(client_id):
        return next(Client.query(client_id))

    @oauth.grantgetter
    def get_grant(client_id, code):
        return next(Grant.query(client_id, code))

    @oauth.tokengetter
    def get_token(access_token=None, refresh_token=None):
        if access_token:
            return next(Token.query(access_token))
        # if refresh_token:
        #     return next(Token.query(refresh_token=refresh_token))
        return None

    @oauth.grantsetter
    def set_grant(client_id, code, request, *args, **kwargs):
        expires = datetime.utcnow() + timedelta(seconds=120000)
        redirect_params = {'code': code['code'], 'state': request.state}
        redirect_uri = '{}?{}'.format(request.redirect_uri, urllib.urlencode(redirect_params))
        grant = Grant(
            client_id=client_id,
            code=code['code'],
            redirect_uri=redirect_uri,
            scope=' '.join(request.scopes),
            userId=g.user.userId,
            expires=expires,
        )
        print(grant.__dict__)
        grant.save()

    @oauth.tokensetter
    def set_token(token, request, *args, **kwargs):
        tok = Token(**token)
        tok.userId = request.user.userId
        tok.client_id = request.client.client_id
        tok.save()

    return oauth
