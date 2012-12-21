from babelpr.commands import ExplicitCommand
from babelpr import Message
from babelpr.chatbot import ChatBot
from babelpr.utils import getWebpage
import re


class ChampionselectCommand(ExplicitCommand):
    
    def __init__(self, chatbot):
        ExplicitCommand.__init__(self, chatbot)
        
        self.triggers = ['championselect','champselect','counters']
        self.name = 'championselect'
        self.description = "Checks championselect.net for strong/weak LoL champion matchups"
        self.syntax = "#championselect CHAMPION"
        
        counter_pattern = '<h3 class="counterName">(?P<champ>[^<]+)</h3>'
        self.re_counter = re.compile(counter_pattern)
        
        champ_pattern = '<h2>(?P<champ>.+?) is strong against</h2>'
        self.re_champ = re.compile(champ_pattern)
        

    def processCommand(self, message, trigger, arguments):
        assert isinstance(message, Message.Message)
        assert isinstance(self._chatbot, ChatBot)
        
        arguments = arguments.strip()
        if len(arguments) == 0:
            return "Syntax: " + self.syntax
        
        url = "http://www.championselect.net/champ/"+arguments
        data = getWebpage(url)
        
        r = self.re_champ.search(data)
        if not r:
            return "Sorry, I couldn't find info for '%s'" % arguments
        
        champ_name = r.groupdict()['champ']
            
        
        parts = data.split('is strong against</h2>',1)
        weak = self.re_counter.findall(parts[0])
        strong = self.re_counter.findall(parts[1])
        
        weak_str = ", ".join(weak[:5])
        strong_str = ", ".join(strong[:5])
        ret = "%s is strong against %s, but weak against %s" % (champ_name, strong_str, weak_str)
        
        return ret