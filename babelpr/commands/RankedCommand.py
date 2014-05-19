from babelpr import Message
from babelpr.LeagueOfLegends.KassadinSummoner import KassadinSummoner
from babelpr.LeagueOfLegends.LolkingSummoner import LolkingSummoner
from babelpr.commands import ExplicitCommand

class RankedCommand(ExplicitCommand):
    
    def __init__(self, chatbot):
        ExplicitCommand.__init__(self, chatbot)
        
        self.triggers = ['ranked']
        self.name = 'ranked'
        self.description = "Gives you ranked game stats for a summoner on a champion"
        self.syntax = "#ranked SUMMONERNAME,CHAMPIONNAME"
    
    def processCommand(self, message, trigger, arguments):
        assert isinstance(message, Message.Message)
        
        arg_parts = arguments.split(',')
        if len(arg_parts) != 2:
            return "Invalid syntax.  Usage: %s" % self.syntax
        
        summoner_name = arg_parts[0].strip()        
        champion_name = arg_parts[1].strip()        
        
        ranked_stats = None
        providers = [LolkingSummoner, KassadinSummoner]
        for provider in providers:
            try:
                summoner = provider(arguments, self._chatbot)
                ranked_stats = summoner.getLastMatch(champion_name)
            except:
                ranked_stats = None

            if ranked_stats is not None:
                break

        if ranked_stats is None:
            return "No ranked stats for '%s' on '%s' could be found. Check the summoner and champion names, or try again later" % (summoner_name, champion_name)
            
        return ranked_stats.toString()
