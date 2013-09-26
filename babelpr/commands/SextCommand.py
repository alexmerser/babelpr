from babelpr.commands import RandomCSVResponseExplicitCommand

class SextCommand(RandomCSVResponseExplicitCommand):
    
    def __init__(self, chatbot):
        RandomCSVResponseExplicitCommand.__init__(self, chatbot)
        
        self.triggers = ['sext', 'cyb0r', 'cyber', 'cybor']
        self.name = "sext"
        self.description = "Talks dirty to you."
        self.syntax = "#sext"
