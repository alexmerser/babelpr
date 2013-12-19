from babelpr.commands import RandomResponseExplicitCommand

class CraigCommand(RandomResponseExplicitCommand):
    
    def __init__(self, chatbot):
        RandomResponseExplicitCommand.__init__(self, chatbot)
        
        self.triggers = ['craig']
        self._responses = ['dolla dolla bills, y\'all']
        self.name = "craig"
        self.description = "1%"
        self.syntax = "#craig"