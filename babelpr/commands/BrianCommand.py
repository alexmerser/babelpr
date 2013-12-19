from babelpr.commands import RandomResponseExplicitCommand

class BrianCommand(RandomResponseExplicitCommand):
    
    def __init__(self, chatbot):
        RandomResponseExplicitCommand.__init__(self, chatbot)
        
        self.triggers = ['brian']
        self._responses = ['LAB TIME', 'free food time']
        self.name = "brian"
        self.description = "Dr. Uncle Brian, BDC"
        self.syntax = "#brian"