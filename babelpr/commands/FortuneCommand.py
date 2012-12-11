from babelpr.commands import RandomDatabaseResponseExplicitCommand

class FortuneCommand(RandomDatabaseResponseExplicitCommand):
    
    def __init__(self, chatbot):
        RandomDatabaseResponseExplicitCommand.__init__(self, chatbot)
        
        self.triggers = ['fortune']
        self.name = "fortune"
        self.description = "Tells you your fortune."
        self.syntax = "#fortune"
