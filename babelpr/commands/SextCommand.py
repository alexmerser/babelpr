from babelpr.commands import RandomDatabaseResponseExplicitCommand

class SextCommand(RandomDatabaseResponseExplicitCommand):
    
    def __init__(self, chatbot):
        RandomDatabaseResponseExplicitCommand.__init__(self, chatbot)
        
        self.triggers = ['sext', 'cyb0r', 'cyber', 'cybor']
        self.name = "sext"
        self.description = "Talks dirty to you."
        self.syntax = "#sext"
