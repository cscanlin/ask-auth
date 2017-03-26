from datetime import datetime, timedelta
import logging

from flask import Flask, g, render_template, jsonify, make_response, request
from flask_ask import Ask, statement, request as ask_request, session
from flask_oauthlib.provider import OAuth2Provider

from models import AlexaUser, Client, Grant, Token

def speech_response(speech_text):
    logger.info(speech_text)
    return statement(speech_text).simple_card(ask_request.type, speech_text)

def default_provider(app):
    oauth = OAuth2Provider(app)

    @oauth.clientgetter
    def get_client(client_id):
        return Client.query.filter_by(client_id=client_id).first()

    @oauth.grantgetter
    def get_grant(client_id, code):
        return Grant.query.filter_by(client_id=client_id, code=code).first()

    @oauth.tokengetter
    def get_token(access_token=None, refresh_token=None):
        if access_token:
            return Token.query.filter_by(access_token=access_token).first()
        if refresh_token:
            return Token.query.filter_by(refresh_token=refresh_token).first()
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
        # NOTICE: for real project, you need to require login
        if request.method == 'GET':
            # render a page for user to confirm the authorization
            return render_template('confirm.html')

        if request.method == 'HEAD':
            # if HEAD is supported properly, request parameters like
            # client_id should be validated the same way as for 'GET'
            response = make_response('', 200)
            response.headers['X-Client-ID'] = kwargs.get('client_id')
            return response

        confirm = request.form.get('confirm', 'no')
        return confirm == 'yes'

    @app.route('/oauth/token', methods=['POST', 'GET'])
    @oauth.token_handler
    def access_token():
        return {}

    @app.route('/oauth/revoke', methods=['POST'])
    @oauth.revoke_handler
    def revoke_token():
        pass

    @oauth.invalid_response
    def require_oauth_invalid(req):
        return jsonify(message=req.error_message), 401

    return app

def bind_ask_handlers(ask):
    @ask.intent('IntroduceIntent')
    def introduce(name):
        user = AlexaUser(
            userId=session.user.userId,
            name=name,
        )
        user.save()
        speech_text = 'Confirmed name as {}'.format(user.name)
        return speech_response(speech_text)

    @ask.intent('HelloIntent')
    def hello():
        user = next(AlexaUser.query(session.user.userId))
        speech_text = 'Hello {}'.format(user.name) if user else 'Hello. Please introduce yourself'
        return speech_response(speech_text)

    return ask

if __name__ == '__main__':
    logger = logging.getLogger('flask_ask')
    logger.setLevel(logging.DEBUG)

    app = Flask(__name__)
    ask = Ask(app, '/')

    app = create_server(app)
    ask = bind_ask_handlers(ask)

    app.run(debug=True)
