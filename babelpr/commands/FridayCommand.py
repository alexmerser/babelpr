from babelpr.commands import RandomResponseExplicitCommand

class FridayCommand(RandomResponseExplicitCommand):
    
    def __init__(self, chatbot):
        RandomResponseExplicitCommand.__init__(self, chatbot)
        
        self.triggers = ['friday']
        self._responses = ['FRIDAY FRIDAY, GOTTA GET DOWN ON FRIDAY']

