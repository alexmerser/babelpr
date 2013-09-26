from babelpr.commands import RandomCSVResponseExplicitCommand

class FortuneCommand(RandomCSVResponseExplicitCommand):
    
    def __init__(self, chatbot):
        RandomCSVResponseExplicitCommand.__init__(self, chatbot)
        
        self.triggers = ['fortune']
        self.name = "fortune"
        self.description = "Tells you your fortune."
        self.syntax = "#fortune"
