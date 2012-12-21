from babelpr.commands import ExplicitCommand
from babelpr import Message
from babelpr.chatbot import ChatBot
from babelpr.libs.chatterbotapi import ChatterBotFactory, ChatterBotType


class ChatCommand(ExplicitCommand):
    
    def __init__(self, chatbot):
        ExplicitCommand.__init__(self, chatbot)
        
        self.triggers = ['chat']
        self.name = 'chat'
        self.description = "Chat with the bot"
        self.syntax = "#chat SAYSOMETHINGHEREDUMBASS"
        
        self._clever = ChatterBotFactory().create(ChatterBotType.CLEVERBOT)
        self._clever_session = self._clever.create_session()
        

    def processCommand(self, message, trigger, arguments):
        assert isinstance(message, Message.Message)
        assert isinstance(self._chatbot, ChatBot)
        
        arguments = arguments.strip()
        if len(arguments) == 0:
            return "What did you want to chat about?"
        
        return self._clever_session.think(arguments)