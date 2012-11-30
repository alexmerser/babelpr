from babelpr.commands import TriggeredCommand
from babelpr import Message
from babelpr.chatbot import ChatBot
from babelpr.globals import BabelGlobals
import sqlite3

class AddCommand(TriggeredCommand):
    triggers = ['add']

    def processCommand(self, message, arguments):
        assert isinstance(message, Message.Message)
        assert isinstance(self._chatbot, ChatBot)
        
        arg_parts = arguments.split(' ', 1)
        if len(arg_parts) != 2:
            return "Invalid syntax.  Usage: #add DATABASE RESPONSE"
        
        selected_command = None
        for trigger,command in self._chatbot._triggered_commands.iteritems():
            if trigger == arg_parts[0]:
                selected_command = command
                break
        
        if selected_command is None:
            return "Unknown command/database: '%s'" % arg_parts[0]
        
        command_name = selected_command.__class__.__name__
        database_name = command_name.lower()[0:-7]
        database_file = BabelGlobals.location + '/babelpr/commands/databases/'+database_name+'.db'
        
        success = False
        try:
            connection = sqlite3.connect(database_file)
            cursor = connection.cursor()
            cursor.execute('insert into responses values (?)', [arg_parts[1]])
            success = True
        except:
            success = False
            
        try:
            cursor.close()
            connection.close()
        except:
            pass
        
        response = "Response added to '%s'" % arg_parts[0] if success else "Failed to add response.  Sorry."
        
        return response
            
        
    