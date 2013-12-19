from babelpr.commands import ExplicitCommand
from babelpr import Message
from babelpr.chatbot import ChatBot
from xml.dom import minidom
import time
import datetime


class SteamstatusCommand(ExplicitCommand):
    
    def __init__(self, chatbot):
        ExplicitCommand.__init__(self, chatbot)
        
        self.triggers = ['steamstatus']
        self.name = 'steamstatus'
        self.description = "Gets status of a Steam user"
        self.syntax = "#steamstatus STEAMNICK"

    def processCommand(self, message, trigger, arguments):
        assert isinstance(message, Message.Message)
        assert isinstance(self._chatbot, ChatBot)
        
        arguments = arguments.strip()
        if len(arguments) == 0:
            return "A steam nick is required.  Syntax: %s" % self.syntax
        
        medium_alias = "steam"
        if not self._chatbot._mediums.has_key(medium_alias):
            return "I am not set up to connect to Steam"
        
        medium = self._chatbot._mediums[medium_alias]
        online = medium.getRoster()

        user_data = None
        for data in online.itervalues():
            if data['name'].lower() == arguments.lower():
                user_data = data
                break
                
        if user_data is None:
            return "Steam user '%s' is offline (or not friends with %s)" % (arguments, medium._config['bot_nick'])
        
        if user_data['currently_playing'] is not None:
            return "%s is logged on to Steam playing %s" % (user_data['name'], user_data['currently_playing'])
        
        return "%s is logged on to Steam" % user_data['name']
        
