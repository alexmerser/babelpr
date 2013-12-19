from babelpr.commands import RandomResponseExplicitCommand

class ObeCommand(RandomResponseExplicitCommand):
    
    def __init__(self, chatbot):
        RandomResponseExplicitCommand.__init__(self, chatbot)
        
        self.triggers = ['obe']
        self._responses = ['maple syrup', 'Hey james (blah blah sportsball)']
        self.name = "obe"
        self.description = "America's Hat"
        self.syntax = "#obe"