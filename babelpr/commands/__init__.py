from babelpr import Message
import random
from babelpr.globals import BabelGlobals
from babelpr.logger import Logger
import sqlite3

class Command(object):
    name = None
    triggers = []
    description = None
    syntax = None
    
    _chatbot = None
    
    def __init__(self, chatbot):
        self._chatbot = chatbot
    

class TriggeredCommand(Command):
    def processCommand(self, message, trigger, arguments):
        assert isinstance(message, Message.Message)
        return None

class GreedyCommand(Command):
    def processMessage(self, message):
        assert isinstance(message, Message.Message)
        return None


class PhraseResponseCommand(GreedyCommand):
    _phrases = []
    _responses = []
    
    def processMessage(self, message):
        super(PhraseResponseCommand, self).processMessage(message)
        assert isinstance(message, Message.Message)
        
        if message.body in self._phrases:
            i = random.randint(0,len(self._responses)-1)
            selected = self._responses[i]
            return selected
        
        return None
    
class RandomResponseCommand(TriggeredCommand):
    _responses = []
    
    def processCommand(self, message, trigger, arguments):
        super(RandomResponseCommand, self).processCommand(message, trigger, arguments)
        assert isinstance(message, Message.Message)
        
        if len(self._responses) == 0:
            return None
        
        i = random.randint(0,len(self._responses)-1)
        selected = self._responses[i]
        return selected
    
class RandomDatabaseResponseCommand(RandomResponseCommand):
    _database_file = None
    _db = None
    
    def __init__(self, chatbot):
        super(RandomDatabaseResponseCommand, self).__init__(chatbot)
        
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
    
