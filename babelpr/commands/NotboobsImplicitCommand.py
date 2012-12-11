from babelpr.commands import ExactPhraseImplicitCommand

class NotboobsImplicitCommand(ExactPhraseImplicitCommand):
    
    def __init__(self, chatbot):
        ExactPhraseImplicitCommand.__init__(self, chatbot)
        
        self._phrases = ['!boobs']
        self._responses = [':(']
