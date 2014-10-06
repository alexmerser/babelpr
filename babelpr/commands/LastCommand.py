from babelpr import Message
from babelpr.LeagueOfLegends.KassadinSummoner import KassadinSummoner
from babelpr.LeagueOfLegends.LolkingSummoner import LolkingSummoner
from babelpr.LeagueOfLegends.OpggSummoner import OpggSummoner
from babelpr.LeagueOfLegends.RiotApiSummoner import RiotApiSummoner
from babelpr.commands import ExplicitCommand
import exceptions, logging, sys

class LastCommand(ExplicitCommand):
    
    def __init__(self, chatbot):
        ExplicitCommand.__init__(self, chatbot)
        
        self.triggers = ['last']
        self.name = 'last'
        self.description = "Tells you info about the last game a summoner played"
        self.syntax = "#last SUMMONERNAME[,SKIP_NUM]"
    
    def processCommand(self, message, trigger, arguments):
        assert isinstance(message, Message.Message)
        
        arg_parts = arguments.split(',')
        if len(arg_parts) > 2:
            return "Invalid syntax.  Usage: %s" % self.syntax
        
        summoner_name = arg_parts[0].strip()        
        if len(arg_parts) == 2:
            try:
                skip_num = int(arg_parts[1].strip())
            except exceptions.ValueError:
                return "Invalid syntax.  Usage: %s" % self.syntax
        else:
            skip_num = 0 
        
        last_match = None
        providers = [RiotApiSummoner]
        for provider in providers:
            try:
                summoner = provider(arg_parts[0], self._chatbot)
                last_match = summoner.getLastMatch(skip_num)
            except:
                logging.exception("Provider exception in getLastMatch")
                print sys.exc_info()[0]
                last_match = None

            if last_match is not None:
                break
        
        if last_match is None:
            return "Recent match for '%s' was not found or was invalid. Check the summoner name or try again later" % summoner_name
            
        return last_match.toString()
