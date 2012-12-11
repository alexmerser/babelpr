from babelpr.commands import RandomResponseExplicitCommand

class JamesrosserCommand(RandomResponseExplicitCommand):
    
    def __init__(self, chatbot):
        RandomResponseExplicitCommand.__init__(self, chatbot)
        
        self.triggers = ['jamesrosser']
        self._responses = ['8=====================================================================================================================================================================================================D']
        self.name = "jamesrosser"
        self.description = "... have you seen it?"
        self.syntax = "#jamesrosser"