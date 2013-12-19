from babelpr.commands import RandomResponseExplicitCommand

class HankCommand(RandomResponseExplicitCommand):
    
    def __init__(self, chatbot):
        RandomResponseExplicitCommand.__init__(self, chatbot)
        
        self.triggers = ['hank']
        self._responses = ['goddamnit doug']
        self.name = "hank"
        self.description = "Roll Tide"
        self.syntax = "#hank"