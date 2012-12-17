from babelpr.commands import ExplicitCommand
from babelpr.globals import BabelGlobals
import sqlite3
import random

class InsultCommand(ExplicitCommand):
    
    def __init__(self, chatbot):
        ExplicitCommand.__init__(self, chatbot)


        self._database_file = None
        self._db = None
        command = self.__class__.__name__
        command = command.lower()[0:-7]
        if(self._database_file is None):
            self._database_file = BabelGlobals.location + '/babelpr/commands/databases/'+command+'.db'
        
        self._noun_list = []
        self._adj_list = []
        
        try:
            connection = sqlite3.connect(self._database_file)
            
            cursor = connection.cursor()
            cursor.execute('SELECT noun FROM insult_noun')
            data = cursor.fetchall()
            self._noun_list = [elt[0] for elt in data]
            cursor.close()
            
            cursor = connection.cursor()
            cursor.execute('SELECT adj FROM insult_adj')
            data = cursor.fetchall()
            self._adj_list = [elt[0] for elt in data]
            cursor.close()
        except:
            pass
            
        try:
            connection.close()
        except:
            pass
    
        self.triggers = ['insult']
        self.name = "insult"
        self.description = "Generates a random insult"
        self.syntax = "#insult [person]"

    def processCommand(self, message, trigger, arguments):
        if len(self._noun_list) == 0 or len(self._adj_list) == 0:
            return None
        
        
        arguments = arguments.strip()
        if len(arguments) == 0:
            base = "You are a "
        else:
            base = "%s is a " % arguments
            
        noun = self._noun_list[random.randint(0,len(self._noun_list)-1)]
        adj1 = self._adj_list[random.randint(0,len(self._adj_list)-1)]
        adj2 = self._adj_list[random.randint(0,len(self._adj_list)-1)]
        adj3 = self._adj_list[random.randint(0,len(self._adj_list)-1)]
        insult = "%s, %s, %s %s!" % (adj1, adj2, adj3, noun)
            
            
        return base + insult
        