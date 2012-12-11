from babelpr.commands import ExplicitCommand
from babelpr import Message
from babelpr.chatbot import ChatBot

class HelpCommand(ExplicitCommand):
    
    def __init__(self, chatbot):
        ExplicitCommand.__init__(self, chatbot)
        
        self.triggers = ['help']
        self.name = 'help'
        self.description = "Provides help for commands that are available"
        self.syntax = "#help [COMMAND]"

    def processCommand(self, message, trigger, arguments):
        assert isinstance(message, Message.Message)
        assert isinstance(self._chatbot, ChatBot)
        
        arguments = arguments.strip()
        
        if len(arguments) == 0:
            commands = []
            for trigger,command in self._chatbot._k_commands.iteritems():
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
                
            if not self._chatbot._explicit_commands.has_key(arguments):
                return "Unknown command: '%s'" % arguments
            
            command = self._chatbot._explicit_commands[arguments]
            
            return "Help for command '%(cmd)s':\n%(desc)s\nSyntax: %(syntax)s" % {
                  'cmd': command.name,
                  'desc': command.description,
                  'syntax': command.syntax
            }
             
            
            
