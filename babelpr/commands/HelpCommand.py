from babelpr.commands import TriggeredCommand
from babelpr import Message
from babelpr.chatbot import ChatBot

class HelpCommand(TriggeredCommand):
    triggers = ['help']
    name = 'help'
    description = "Provides help for commands that are available"
    syntax = "#help [COMMAND]"

    def processCommand(self, message, arguments):
        assert isinstance(message, Message.Message)
        assert isinstance(self._chatbot, ChatBot)
        
        arguments = arguments.strip()
        
        if len(arguments) == 0:
            commands = []
            for trigger,command in self._chatbot._triggered_commands.iteritems():
                trigger = command.triggers[0]
                if trigger not in commands:
                    commands.append(trigger)
            commands.sort()
            commands_list = ", ".join(commands)
            return "Available commands: "+commands_list
        else:
            arguments = arguments.lower()
            if arguments[0] == '#':
                arguments = arguments[1:]
                
            if not self._chatbot._triggered_commands.has_key(arguments):
                return "Unknown command: '%s'" % arguments
            
            command = self._chatbot._triggered_commands[arguments]
            
            return "Help for command '%(cmd)s':\n%(desc)s\nSyntax: %(syntax)s" % {
                  'cmd': command.name,
                  'desc': command.description,
                  'syntax': command.syntax
            }
             
            
            
