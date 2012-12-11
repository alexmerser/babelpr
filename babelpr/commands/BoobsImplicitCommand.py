from babelpr.commands import ExactPhraseImplicitCommand

class BoobsImplicitCommand(ExactPhraseImplicitCommand):
    
    def __init__(self, chatbot):
        ExactPhraseImplicitCommand.__init__(self, chatbot)
        
        self._phrases = ['boobs']
        self._responses = ['yum']
