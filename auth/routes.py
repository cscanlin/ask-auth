from flask import render_template, jsonify, request

from models import Client

def bind_auth_routes(app, oauth=None):

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

    @app.route('/privacy_policy', methods=['GET'])
    def privacy_policy():
        return render_template('privacy_policy.html')

    return app
