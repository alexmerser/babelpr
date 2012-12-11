from babelpr.commands import RandomDatabaseResponseExplicitCommand

class JackCommand(RandomDatabaseResponseExplicitCommand):
    
    def __init__(self, chatbot):
        RandomDatabaseResponseExplicitCommand.__init__(self, chatbot)

        self.triggers = ['jack']
        self.name = "jack"
        self.description = "Tells you a random deep thought."
        self.syntax = "#jack"
