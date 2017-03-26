from datetime import datetime, timedelta


from flask import g, render_template, jsonify, request
from flask_oauthlib.provider import OAuth2Provider

from models import Client, Grant, Token

def default_provider(app):
    oauth = OAuth2Provider(app)

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
        grant = Grant(
            client_id=client_id,
            code=code['code'],
            redirect_uri=request.redirect_uri,
            scope=' '.join(request.scopes),
            user_id=g.user.id,
            expires=expires,
        )
        grant.save()

    @oauth.tokensetter
    def set_token(token, request, *args, **kwargs):
        # In real project, a token is unique bound to user and client.
        # Which means, you don't need to create a token every time.
        tok = Token(**token)
        tok.user_id = request.user.id
        tok.client_id = request.client.client_id
        tok.save()

    return oauth

def create_server(app, oauth=None):
    if not oauth:
        oauth = default_provider(app)

    @app.route('/oauth/authorize', methods=['GET', 'POST'])
    @oauth.authorize_handler
    def authorize(*args, **kwargs):
        if request.method == 'GET':
            kwargs['client'] = next(Client.query(kwargs.get('client_id')))
            return render_template('oauthorize.html', **kwargs)

        confirm = request.form.get('confirm', 'no')
        return confirm == 'yes'

    @app.route('/oauth/token', methods=['POST', 'GET'])
    @oauth.token_handler
    def access_token():
        return {}

    @oauth.invalid_response
    def require_oauth_invalid(req):
        return jsonify(message=req.error_message), 401

    return app
