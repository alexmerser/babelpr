from babelpr.commands import RandomResponseExplicitCommand

class IsaacCommand(RandomResponseExplicitCommand):
    
    def __init__(self, chatbot):
        RandomResponseExplicitCommand.__init__(self, chatbot)
        
        self.triggers = ['isaac']
        self._responses = ['at least you didn\'t have to live with ian']
        self.name = "isaac"
        self.description = "Fan of all types of Janna"
        self.syntax = "#isaac"