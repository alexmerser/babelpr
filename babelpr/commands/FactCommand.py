from babelpr.commands import RandomDatabaseResponseExplicitCommand

class FactCommand(RandomDatabaseResponseExplicitCommand):
    
    def __init__(self, chatbot):
        RandomDatabaseResponseExplicitCommand.__init__(self, chatbot)
    
        self.triggers = ['fact']
        self.name = "fact"
        self.description = "Tells you a random fact."
        self.syntax = "#fact"
