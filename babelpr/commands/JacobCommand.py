from babelpr.commands import RandomResponseExplicitCommand

class JacobCommand(RandomResponseExplicitCommand):
    
    def __init__(self, chatbot):
        RandomResponseExplicitCommand.__init__(self, chatbot)
        
        self.triggers = ['jacob']
        self._responses = ['nasos pls']
        self.name = "jacob"
        self.description = "loves mmos"
        self.syntax = "#jacob"