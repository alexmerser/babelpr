from babelpr.commands import RandomDatabaseResponseExplicitCommand

class MitchCommand(RandomDatabaseResponseExplicitCommand):
    
    def __init__(self, chatbot):
        RandomDatabaseResponseExplicitCommand.__init__(self, chatbot)

        self.triggers = ['mitch']
        self.name = "mitch"
        self.description = "Provides a random quote from Mitch Hedberg."
        self.syntax = "#mitch"
