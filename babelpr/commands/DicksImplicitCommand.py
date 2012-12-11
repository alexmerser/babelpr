from babelpr.commands import ExactPhraseImplicitCommand

class DicksImplicitCommand(ExactPhraseImplicitCommand):
    
    def __init__(self, chatbot):
        ExactPhraseImplicitCommand.__init__(self, chatbot)
    
        self._phrases = ['dicks']
        self._responses = ['lol']
