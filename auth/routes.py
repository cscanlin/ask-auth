from flask import render_template, jsonify, request

from models import Client

import logging

logger = logging.getLogger('flask_ask')

def bind_auth_routes(app, oauth=None):

    @app.route('/oauth/authorize', methods=['GET', 'POST'])
    @oauth.authorize_handler
    def authorize(*args, **kwargs):
        logger.debug('authorize_handler')
        if request.method == 'GET':
            kwargs['client'] = next(Client.query(kwargs.get('client_id')))
            kwargs['scope'] = 'ask-auth-dev'
            return render_template('oauthorize.html', **kwargs)

        confirm = request.form.get('confirm', 'no')
        return confirm == 'yes'

    @app.route('/oauth/token', methods=['POST', 'GET'])
    @oauth.token_handler
    def access_token():
        logger.debug('token_handler')
        print(request.__dict__)
        return None

    @oauth.invalid_response
    def require_oauth_invalid(req):
        return jsonify(message=req.error_message), 401

    @app.route('/privacy_policy', methods=['GET'])
    def privacy_policy():
        return render_template('privacy_policy.html')

    return app
