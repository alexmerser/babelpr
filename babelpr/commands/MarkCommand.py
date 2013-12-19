from babelpr.commands import RandomResponseExplicitCommand

class MarkCommand(RandomResponseExplicitCommand):
    
    def __init__(self, chatbot):
        RandomResponseExplicitCommand.__init__(self, chatbot)
        
        self.triggers = ['mark']
        self._responses = ['bro do you even bitcoin']
        self.name = "mark"
        self.description = "Marky mark"
        self.syntax = "#mark"