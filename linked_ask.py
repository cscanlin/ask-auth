import logging

from flask import Flask, g
from flask_ask import Ask, statement, request

from auth import AlexaUser, default_provider, bind_auth_routes

app = Flask(__name__)
ask = Ask(app, '/')
oauth = default_provider(app)

app = bind_auth_routes(app, oauth)

logger = logging.getLogger('flask_ask')
logger.setLevel(logging.DEBUG)

def speech_response(speech_text):
    logger.info(speech_text)
    return statement(speech_text).simple_card(request.type, speech_text) if request else speech_text

@ask.intent('IntroduceIntent')
def introduce(name):
    user = AlexaUser(
        userId=g.user.userId,
        name=name,
    )
    user.save()
    speech_text = 'Confirmed name as {}'.format(user.name)
    return speech_response(speech_text)

@app.route('/hello')
@ask.intent('HelloIntent')
def hello():
    speech_text = 'Hello {}'.format(g.user.name) if g.user and g.user.name else 'Hello. Please introduce yourself'
    return speech_response(speech_text)

if __name__ == '__main__':

    app.run(debug=True)
