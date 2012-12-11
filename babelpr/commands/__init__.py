from babelpr import Message
import random
from babelpr.globals import BabelGlobals
from babelpr.logger import Logger
import sqlite3
import re

class Command(object):
    def __init__(self, chatbot):
        self.name = None
        self.triggers = []
        self.description = None
        self.syntax = None
        self._chatbot = chatbot
    

class ExplicitCommand(Command):
    def processCommand(self, message, trigger, arguments):
        assert isinstance(message, Message.Message)
        return None

class ImplicitCommand(Command):
    def processMessage(self, message):
        assert isinstance(message, Message.Message)
        return None

class RegexImplicitCommand(ImplicitCommand):
    def __init__(self, chatbot):
        ImplicitCommand.__init__(self, chatbot)
        self._patterns = []
        self._regex_flags = 0
        self._regex = None
        
    def initRegex(self):
        self._regex = []
        for pattern in self._patterns:
            self._regex.append(re.compile(pattern, self._regex_flags))
        
    def processMessage(self, message):
        super(RegexImplicitCommand, self).processMessage(message)
        assert isinstance(message, Message.Message)
        
        if self._regex is None:
            self.initRegex()
        
        for regex in self._regex:
            r = regex.search(message.body)
            if r is None:
                continue
            
            groupdict = r.groupdict()
            i = random.randint(0,len(self._responses)-1)
            selected = self._responses[i]
            
            formatter = groupdict
            formatter['sender_nick'] = message.sender_nick
            formatter['body'] = message.body
            
            formatted = selected % formatter
            
            return formatted
        
        return None
    

class ExactPhraseImplicitCommand(ImplicitCommand):
    def __init__(self, chatbot):
        ImplicitCommand.__init__(self, chatbot)
        self._phrases = []
        self._responses = []
    
    def processMessage(self, message):
        super(ExactPhraseImplicitCommand, self).processMessage(message)
        assert isinstance(message, Message.Message)
        
        if message.body in self._phrases:
            i = random.randint(0,len(self._responses)-1)
            selected = self._responses[i]
            return selected
        
        return None
    
class RandomResponseExplicitCommand(ExplicitCommand):
    def __init__(self, chatbot):
        ExplicitCommand.__init__(self, chatbot)
        self._responses = []
    
    def processCommand(self, message, trigger, arguments):
        super(RandomResponseExplicitCommand, self).processCommand(message, trigger, arguments)
        assert isinstance(message, Message.Message)
        
        if len(self._responses) == 0:
            return None
        
        i = random.randint(0,len(self._responses)-1)
        selected = self._responses[i]
        return selected
    
class RandomDatabaseResponseExplicitCommand(RandomResponseExplicitCommand):
    def __init__(self, chatbot):
        super(RandomDatabaseResponseExplicitCommand, self).__init__(chatbot)
        
        self._database_file = None
        self._db = None
        command = self.__class__.__name__
        command = command.lower()[0:-7]
        if(self._database_file is None):
            self._database_file = BabelGlobals.location + '/babelpr/commands/databases/'+command+'.db'
        
        try:
            connection = sqlite3.connect(self._database_file)
            cursor = connection.cursor()
            cursor.execute('SELECT response FROM responses')
            data = cursor.fetchall()
            self._responses = [elt[0] for elt in data]
        except:
            pass
            
        try:
            cursor.close()
            connection.close()
        except:
            pass
    
