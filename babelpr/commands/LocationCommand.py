from babelpr.commands import ExplicitCommand
from babelpr import Message
from babelpr.chatbot import ChatBot
from babelpr.libs.chatterbotapi import ChatterBotFactory, ChatterBotType
from babelpr.utils import isInt


class LocationCommand(ExplicitCommand):
    
    def __init__(self, chatbot):
        ExplicitCommand.__init__(self, chatbot)
        
        self.triggers = ['location']
        self.name = 'location'
        self.description = "Gets or sets your location"
        self.syntax = "#location [ZIPCODE]"
        

    def processCommand(self, message, trigger, arguments):
        assert isinstance(message, Message.Message)
        assert isinstance(self._chatbot, ChatBot)
        
        requestor = self._chatbot.getUniqueIdForSender(message)
        if requestor is None:
            return "Sorry, for some reason I don't know who you are"
        
        arguments = arguments.strip()
        if len(arguments) == 0:
            location = self._chatbot.getUserLocation(requestor)
            if location is None: 
                return "I don't know where you are."
            return "I think you're in '%s'" % location
        
        if not isInt(arguments):
            return "Sorry, I only learn locations that are zipcodes.  Try again with your zipcode."
        
        self._chatbot.storeUserLocation(requestor, arguments)    
        return "Ok, I've learned that you're in '%s'" % arguments
        