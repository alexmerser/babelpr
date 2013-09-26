from babelpr.commands import RandomCSVResponseExplicitCommand

class MitchCommand(RandomCSVResponseExplicitCommand):
    
    def __init__(self, chatbot):
        RandomCSVResponseExplicitCommand.__init__(self, chatbot)

        self.triggers = ['mitch']
        self.name = "mitch"
        self.description = "Provides a random quote from Mitch Hedberg."
        self.syntax = "#mitch"
