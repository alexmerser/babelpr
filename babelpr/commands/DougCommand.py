from babelpr.commands import RandomResponseExplicitCommand

class DougCommand(RandomResponseExplicitCommand):
    
    def __init__(self, chatbot):
        RandomResponseExplicitCommand.__init__(self, chatbot)
        
        self.triggers = ['doug']
        self._responses = ['fuck you hank', 'lets invade', 'jinx jungle is legit, ok?', 'everyone hide in this bush']
        self.name = "doug"
        self.description = "Get on his level"
        self.syntax = "#doug"