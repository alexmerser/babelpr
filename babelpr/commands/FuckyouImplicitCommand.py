from babelpr.commands import RegexImplicitCommand
import re

class FuckyouImplicitCommand(RegexImplicitCommand):
    
    def __init__(self, chatbot):
        RegexImplicitCommand.__init__(self, chatbot)
        self._regex_flags = re.IGNORECASE
        self._patterns = ['^fu(c|ck|k) (yo)?u babel']
        self._responses = ['fuk u %(sender_nick)s']
