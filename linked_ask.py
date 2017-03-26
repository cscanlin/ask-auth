import logging

from flask import Flask
from flask_ask import Ask, statement, request as ask_request, session

from models import AlexaUser
from auth import create_server

app = Flask(__name__)
ask = Ask(app, '/')

app = create_server(app)

logger = logging.getLogger('flask_ask')
logger.setLevel(logging.DEBUG)

def speech_response(speech_text):
    logger.info(speech_text)
    return statement(speech_text).simple_card(ask_request.type, speech_text)

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

    app.run(debug=True)
