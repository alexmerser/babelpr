from babelpr.commands import TriggeredCommand
from babelpr import Message
from babelpr.chatbot import ChatBot

class RosterCommand(TriggeredCommand):
    triggers = ['roster']
    name = 'roster'
    description = "Gets the roster in a given chat medium"
    syntax = "#roster [MEDIUM]"

    def processCommand(self, message, arguments):
        assert isinstance(message, Message.Message)
        assert isinstance(self._chatbot, ChatBot)
        
        arguments = arguments.strip().lower()
        medium_alias = arguments if len(arguments) > 0 else message.medium_alias
        
        if not self._chatbot._mediums.has_key(medium_alias):
            return "Unknown medium: '%s'" % medium_alias
        
        medium = self._chatbot._mediums[medium_alias]
        roster = medium.getRoster()
        users = []
        for id,data in roster.iteritems():
            specialChar = '*' if data['special'] else ''
            users.append(unicode(data['name'] + specialChar))
            
        users.sort(key=unicode.lower)
        
        return ", ".join(users)
            
        
    