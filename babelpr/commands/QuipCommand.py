from babelpr.commands import RandomDatabaseResponseExplicitCommand

class QuipCommand(RandomDatabaseResponseExplicitCommand):
    
    def __init__(self, chatbot):
        RandomDatabaseResponseExplicitCommand.__init__(self, chatbot)
        
        self.triggers = ['quip']
        self.name = "quip"
        self.description = "Says an insightful and/or pun filled quip.  No, it is not a joke"
        self.syntax = "#quip"
