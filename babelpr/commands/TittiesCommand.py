from babelpr.commands import RandomResponseExplicitCommand

class TittiesCommand(RandomResponseExplicitCommand):
    
    def __init__(self, chatbot):
        RandomResponseExplicitCommand.__init__(self, chatbot)
            
        self.triggers = ['titties']
        self._responses = ["Syntax error: when refering to 'the titties command', command is a verb"]
        self.name = "titties"
        self.description = "Do you really need help with them?"
        self.syntax = "#titties"
