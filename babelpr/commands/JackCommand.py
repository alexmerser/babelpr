from babelpr.commands import RandomCSVResponseExplicitCommand

class JackCommand(RandomCSVResponseExplicitCommand):
    
    def __init__(self, chatbot):
        RandomCSVResponseExplicitCommand.__init__(self, chatbot)

        self.triggers = ['jack']
        self.name = "jack"
        self.description = "Tells you a random deep thought."
        self.syntax = "#jack"
