from babelpr.commands import RandomCSVResponseExplicitCommand

class FactCommand(RandomCSVResponseExplicitCommand):
    
    def __init__(self, chatbot):
        RandomCSVResponseExplicitCommand.__init__(self, chatbot)
    
        self.triggers = ['fact']
        self.name = "fact"
        self.description = "Tells you a random fact."
        self.syntax = "#fact"
