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
        
# ------------------------------------------------------------------------------
#
# INTENT HANDLER FUNCTIONS
#
#-------------------------------------------------------------------------------

"""
Handles response to how the user is feeling (either "good" or "bad")
    - Check location in skill progress: makes sure no other answers have been recorded yet (session attributes)
        - If other answers have been recorded, user invoked the wrong intent at the wrong time
    - Adds current response "good" or "bad" to feeling question, then asks next question
"""
def handleFeelingIntent(handler_input):
    logger.info("In handleFeelingIntent") # logs current location in skill
    session_attr = handler_input.attributes_manager.session_attributes # grabs session attributes
    if not bool(session_attr): # in python, session attributes are stored in a dictionary, resolves to FALSE when empty
        session_attr
        handler_input.response_builder.ask(FEELING_REPROMPT) # adds attributes to response
        return handler_input.response_builder.response # builds and returns response
    else:
        handler_input.response_builder.ask("hmm not what I wanted") # adds attributes to response. need to redirect to error handler
        return handler_input.response_builder.response # builds and returns response

def handleWeatherIntent(handler_input):
    logger.info("In handleWeatherIntent") # logs current location in skill
    session_attr = handler_input.attributes_manager.session_attributes # grabs session attributes
    if "weather" in session_attr and "wake" not in session_attr:
        handler_input.response_builder.ask(WEATHER_REPROMPT) # adds attributes to response
        return handler_input.response_builder.response # builds and returns response
    else:
        handler_input.response_builder.ask("hmm not what I wanted") # adds attributes to response. need to redirect to error handler
        return handler_input.response_builder.response # builds and returns response

def handleWakeIntent(handler_input):
    logger.info("In handleWakeIntent") # logs current location in skill
    session_attr = handler_input.attributes_manager.session_attributes # grabs session attributes
    if "weather" in session_attr and "wake" in session_attr:
        return conclusion(handler_input)
    else:
        handler_input.response_builder.ask("hmm not what I wanted") # adds attributes to response. need to redirect to error handler
        return handler_input.response_builder.response # builds and returns response

# ------------------------------------------------------------------------------
#
# HELPER FUNCTIONS
#
#-------------------------------------------------------------------------------

def conclusion(handler_input):
    logger.info("In conclusion") # logs current location in skill

# ------------------------------------------------------------------------------
#
# ADDING HANDLERS TO SKILL
#
#-------------------------------------------------------------------------------

skill_builder = SkillBuilder()

# Add all request handlers to the skill.
skill_builder.add_request_handler(LaunchRequestHandler())
skill_builder.add_request_handler(IntentRequestHandler())
#sb.add_request_handler(InProgressPetMatchIntent()) #change 
#sb.add_request_handler(CompletedPetMatchIntent()) #change
#sb.add_request_handler(HelpIntentHandler())
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
