from babelpr.commands import RandomResponseExplicitCommand

class TittiesCommand(RandomResponseExplicitCommand):
    
    def __init__(self, chatbot):
        RandomResponseExplicitCommand.__init__(self, chatbot)
            
        self.triggers = ['titties']
        self._responses = ["I have nipples, Greg, could you milk me?"]
        self.name = "titties"
        self.description = "Do you really need help with them?"
        self.syntax = "#titties"
