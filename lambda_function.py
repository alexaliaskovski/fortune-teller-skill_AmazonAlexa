# Alexa Liaskovski
# fortunes taken from here: http://www.fortunecookiemessage.com/archive.php
# ------------------------------------------------------------------------------
#
# IMPORTS
#
#-------------------------------------------------------------------------------

import json
import logging

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractExceptionHandler, AbstractResponseInterceptor, AbstractRequestInterceptor
from ask_sdk_core.utils import is_intent_name, is_request_type, get_slot_value
from ask_sdk_model import Response, IntentRequest, DialogState, SlotConfirmationStatus, Slot
from ask_sdk_model.slu.entityresolution import StatusCode

# logger will log different states the function is in when certain functions are triggered.
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ------------------------------------------------------------------------------
#
# DATA
#
#-------------------------------------------------------------------------------

# Text
LAUNCH_SPEECH = 'Welcome to the fortune teller! I will tell you your fortune after a few easy questions.'
LAUNCH_REPROMPT = 'How are you feeling today? Good or bad?'
FEELING_REPROMPT = 'Is the weather nice or bad today?'
WEATHER_REPROMPT = 'Did you wake up early or late this morning?'

# Fortune dictionary
# maybe change keys in dictionary
FORTUNE = {
    "good-nice-early": "Today it's up to you to create the peacefulness you long for.",
    "good-nice-late": "A friend asks only for your time not your money.",
    "good-bad-early": "If you refuse to accept anything but the best, you very often get it.",
    "good-bad-late": "A smile is your passport into the hearts of others.",
    "bad-nice-early": "A good way to keep healthy is to eat more Chinese food.",
    "bad-nice-late": "Your high-minded principles spell success.",
    "bad-bad-early" : "Hard work pays off in the future, laziness pays off now.",
    "bad-bad-late": "Change can hurt, but it leads a path to something better."
}

# Help dictionary, to find what kind of help to give based on most recent question.
# gross and hard-coded...
HELP_DICT = {
    LAUNCH_REPROMPT : "Respond good if you're feeling good today, or bad if you're feeling bad today. If you're not sure, pick one at random.",
    FEELING_REPROMPT : "Respond nice if you like the weather outside today, or bad if you don't like the weather outside today. If you're not sure, pick one at random.",
    WEATHER_REPROMPT : "Respond early if you woke up earlier than usual or on time, or late if you woke up later than usual or later than you should have. If you're not sure, pick one at random."
}

# ------------------------------------------------------------------------------
#
# HANDLER CLASSES
#
#-------------------------------------------------------------------------------

"""  
Handles LAUNCH requests.
    function can_handle: will return TRUE if request type is 'LaunchRequest', otherwise FALSE.
    function handle: sends introduction-to-skill text and reprompt to begin activity.
"""
class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)
    def handle(self, handler_input):
        logger.info("In LaunchRequestHandler") # logs current location in skill
        saveLastSpoken(handler_input, LAUNCH_REPROMPT)
        handler_input.response_builder.speak(LAUNCH_SPEECH).ask(LAUNCH_REPROMPT) # adds attributes to response
        return handler_input.response_builder.response # builds and returns response

"""
Handles INTENT requests.
    function can_handle: will return TRUE if request type is 'IntentRequest', otherwise FALSE.
    function handle: calls appropriate helper function based on intent type.
"""
class IntentRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("IntentRequest")(handler_input)
    def handle(self, handler_input):
        logger.info("In IntentRequestHandler") # logs current location in skill
        if is_intent_name("FeelingIntent")(handler_input):
            return handleFeelingIntent(handler_input)
        elif is_intent_name("WeatherIntent")(handler_input):
            return handleWeatherIntent(handler_input)
        elif is_intent_name("WakeIntent")(handler_input):
            return handleWakeIntent(handler_input)
        else:
            #some kinda error
            pass

"""
Handles HELP requests.
    function can_handle: will return TRUE if request type is 'HelpRequest', otherwise FALSE.
    function handle: sends help to user based on where they are in questions. Reprompts most recent question.
"""
class HelpRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("HelpRequest")(handler_input)
    def handle(self, handler_input):
        logger.info("In HelpRequestHandler") # logs current location in skill
        session_attr = handler_input.attributes_manager.session_attributes # grabs session attributes
        handler_input.response_builder.speak(HELP_DICT[session_attr["last_spoken"]]).reprompt(session_attr["last_spoken"])
        return handler_input.response_builder.response

# ------------------------------------------------------------------------------
#
# INTENT HANDLER FUNCTIONS
#
#-------------------------------------------------------------------------------

"""
Handles response to how the user is feeling (either "good" or "bad")
    - Check location in skill progress: makes sure no other answers have been recorded yet (session attributes)
        - If other answers have been recorded, user invoked the wrong intent at the wrong time
    - Adds current response "good" or "bad" to session attributes, then asks next question
"""
def handleFeelingIntent(handler_input):
    logger.info("In handleFeelingIntent") # logs current location in skill
    session_attr = handler_input.attributes_manager.session_attributes # grabs session attributes
    if not bool(session_attr): # in python, session attributes are stored in a dictionary, resolves to FALSE when empty
        session_attr["feeling"] = get_slot_value(handler_input, "feeling")
        handler_input.response_builder.ask(FEELING_REPROMPT) # adds attributes to response
        saveLastSpoken(handler_input, FEELING_REPROMPT)
        return handler_input.response_builder.response # builds and returns response
    else:
        handler_input.response_builder.ask("hmm not what I wanted").set_should_end_session(True) # adds attributes to response. need to redirect to error handler
        return handler_input.response_builder.response # builds and returns response

"""
Handles response to the weather (either "nice" or "bad")
    - Check location in skill progress: makes sure only feeling answers have been recorded (session attributes)
        - If other answers have been recorded, user invoked the wrong intent at the wrong time
    - Adds current response "nice" or "bad" to session attributes, then asks next question
"""
def handleWeatherIntent(handler_input):
    logger.info("In handleWeatherIntent") # logs current location in skill
    session_attr = handler_input.attributes_manager.session_attributes # grabs session attributes
    if "feeling" in session_attr and "weather" not in session_attr and "wake" not in session_attr: # this is super gross and hardcoded
        session_attr["weather"] = get_slot_value(handler_input, "weather")
        handler_input.response_builder.ask(WEATHER_REPROMPT) # adds attributes to response
        saveLastSpoken(handler_input, WEATHER_REPROMPT)
        return handler_input.response_builder.response # builds and returns response
    else:
        handler_input.response_builder.ask("hmm not what I wanted").set_should_end_session(True) # adds attributes to response. need to redirect to error handler
        return handler_input.response_builder.response # builds and returns response

"""
Handles response to when the user woke up (either "early" or "late")
    - Check location in skill progress: makes sure feeling and weather have been recorded already (session attributes)
        - If other answers have been recorded, user invoked the wrong intent at the wrong time
    - Adds current response "early" or "late" to session attributes, then asks next question
"""
def handleWakeIntent(handler_input):
    logger.info("In handleWakeIntent") # logs current location in skill
    session_attr = handler_input.attributes_manager.session_attributes # grabs session attributes
    if "feeling" in session_attr and "weather" in session_attr and "wake" not in session_attr:
        session_attr["wake"] = get_slot_value(handler_input, "wake")
        return conclusion(handler_input)
    else:
        handler_input.response_builder.ask("hmm not what I wanted").set_should_end_session(True) # adds attributes to response. need to redirect to error handler
        return handler_input.response_builder.response # builds and returns response

# ------------------------------------------------------------------------------
#
# HELPER FUNCTIONS
#
#-------------------------------------------------------------------------------

"""
Handles conclusion, sends fortune to the user
    - Uses session attributes to build key for FORTUNE dictionary
    - Grabs fortune and sends to user. Terminated session.
"""
def conclusion(handler_input):
    logger.info("In conclusion") # logs current location in skill
    session_attr = handler_input.attributes_manager.session_attributes # grabs session attributes
    key = session_attr["feeling"] + "-" + session_attr["weather"] + "-" + session_attr["wake"]
    handler_input.response_builder.speak("Your fortune is: " + FORTUNE[key]).set_should_end_session(True) # adds attributes to response. need to redirect to error handler
    return handler_input.response_builder.response # builds and returns response
    # could change to reprompt the user to start again

def saveLastSpoken(handler_input, speach):
    session_attr = handler_input.attributes_manager.session_attributes # grabs session attributes
    session_attr["last_spoken"] = speach

# ------------------------------------------------------------------------------
#
# ADDING HANDLERS TO SKILL
#
#-------------------------------------------------------------------------------

skill_builder = SkillBuilder()

# Add all request handlers to the skill.
skill_builder.add_request_handler(LaunchRequestHandler())
skill_builder.add_request_handler(IntentRequestHandler())
skill_builder.add_request_handler(HelpRequestHandler())
#sb.add_request_handler(FallbackIntentHandler())
#sb.add_request_handler(ExitIntentHandler())
#sb.add_request_handler(SessionEndedRequestHandler())

# Add exception handler to the skill.
#sb.add_exception_handler(CatchAllExceptionHandler())

# Add response interceptor to the skill.
#sb.add_global_request_interceptor(RequestLogger())
#sb.add_global_response_interceptor(ResponseLogger())

# Expose the lambda handler to register in AWS Lambda. This is the first function to be called.
lambda_handler = skill_builder.lambda_handler()
