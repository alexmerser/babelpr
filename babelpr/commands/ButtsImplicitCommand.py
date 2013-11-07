from babelpr.commands import ExactPhraseImplicitCommand

class ButtsImplicitCommand(ExactPhraseImplicitCommand):
    
    def __init__(self, chatbot):
        ExactPhraseImplicitCommand.__init__(self, chatbot)
    
        self._phrases = ['butts']
        self._responses = ['pwwwwwwwwt']
