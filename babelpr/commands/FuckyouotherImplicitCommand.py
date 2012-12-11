from babelpr.commands import RegexImplicitCommand
import re

class FuckyouotherImplicitCommand(RegexImplicitCommand):
    
    def __init__(self, chatbot):
        RegexImplicitCommand.__init__(self, chatbot)
        self._regex_flags = re.IGNORECASE
        self._patterns = ['^fu(c|ck|k) (yo)?u (?P<name>((?!babel).*))']
        self._responses = ['yeah, fuck you %(name)s!']
