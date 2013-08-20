from babelpr import Message
from babelpr.LeagueOfLegends.LolkingSummoner import LolkingSummoner
from babelpr.LeagueOfLegends.Summoner import SummonerProfileLoadFailure, \
    UnknownSummoner
from babelpr.LeagueOfLegends.SummonerMatchStats import SummonerMatchStats
from babelpr.commands import ExplicitCommand
import exceptions

class LastCommand(ExplicitCommand):
    
    def __init__(self, chatbot):
        ExplicitCommand.__init__(self, chatbot)
        
        self.triggers = ['last']
        self.name = 'last'
        self.description = "Tells you info about the last game a summoner played"
        self.syntax = "#last SUMMONERNAME[,SKIP_NUM]"
    
    def processCommand(self, message, trigger, arguments):
        assert isinstance(message, Message.Message)
        #assert isinstance(self._chatbot, ChatBot)
        
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
        
        try:
            summoner = LolkingSummoner(summoner_name)
            last_match = summoner.getLastMatch(skip_num)
        except UnknownSummoner:
            return "Unknown summoner: '%s'" % summoner_name
        except SummonerProfileLoadFailure:
            return "Failed to load summoner profile for '%s'" % summoner_name
        #except:
        #    return "Error while attempting to load summoner '%s'" % arguments
            
        if last_match is None:
            return "No recent matches for '%s' found" % summoner_name

        assert isinstance(last_match, SummonerMatchStats)
        
        return last_match.toString()
            
        
    