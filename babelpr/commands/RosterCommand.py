from babelpr.commands import ExplicitCommand
from babelpr import Message
from babelpr.chatbot import ChatBot

class RosterCommand(ExplicitCommand):
    triggers = ['roster', 'lolroster']
    name = 'roster'
    description = "Gets the roster in a given chat medium"
    syntax = "#roster [MEDIUM]"

    def processCommand(self, message, trigger, arguments):
        assert isinstance(message, Message.Message)
        assert isinstance(self._chatbot, ChatBot)
        
        if trigger != 'roster':
            medium_alias = trigger[:-6]
        else:
            arguments = arguments.strip().lower()
            medium_alias = arguments if len(arguments) > 0 else message.medium_alias
        
        if not self._chatbot._mediums.has_key(medium_alias):
            return "Unknown medium: '%s'" % medium_alias
        
        medium = self._chatbot._mediums[medium_alias]
        roster = medium.getRoster()
        users = []
        seen_users = []
        for id,data in roster.iteritems():
            plain_name = "%s" % data['name']
            if plain_name in seen_users:
                continue
            seen_users.append(plain_name)
            
            specialChar = '*' if data['special'] else ''
            users.append(unicode(data['name'] + specialChar))
            
        users.sort(key=unicode.lower)
        
        if len(users) == 0:
            return "Nobody is on."
        
        return ", ".join(users)
            
        
    