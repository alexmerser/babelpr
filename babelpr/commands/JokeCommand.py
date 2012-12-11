from babelpr.commands import RandomDatabaseResponseExplicitCommand

class JokeCommand(RandomDatabaseResponseExplicitCommand):
    
    def __init__(self, chatbot):
        RandomDatabaseResponseExplicitCommand.__init__(self, chatbot)
        
        self.triggers = ['joke']
        self.name = "joke"
        self.description = "Tells you a joke"
        self.syntax = "#jack"
