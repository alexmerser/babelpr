from babelpr.commands import ExactPhraseImplicitCommand

class LolImplicitCommand(ExactPhraseImplicitCommand):
    
    def __init__(self, chatbot):
        ExactPhraseImplicitCommand.__init__(self, chatbot)
        
        self._phrases = ['lol']
        self._responses = [
                      '8==========D',
                      '8=========D',
                      '8========D',
                      '8=======D',
                      '8======D',
                      '8=====D',
                      '8====D',
                      '8===D',
                      '8==D',
                      '8=D'
                      ]
