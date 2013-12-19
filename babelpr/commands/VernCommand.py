from babelpr.commands import RandomResponseExplicitCommand

class VernCommand(RandomResponseExplicitCommand):
    
    def __init__(self, chatbot):
        RandomResponseExplicitCommand.__init__(self, chatbot)
        
        self.triggers = ['vern']
        self._responses = ['lag']
        self.name = "vern"
        self.description = "Asian IRL"
        self.syntax = "#vern"