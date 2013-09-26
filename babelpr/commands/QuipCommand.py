from babelpr.commands import RandomCSVResponseExplicitCommand

class QuipCommand(RandomCSVResponseExplicitCommand):
    
    def __init__(self, chatbot):
        RandomCSVResponseExplicitCommand.__init__(self, chatbot)
        
        self.triggers = ['quip']
        self.name = "quip"
        self.description = "Says an insightful and/or pun filled quip.  No, it is not a joke"
        self.syntax = "#quip"
