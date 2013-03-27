from babelpr import Message
from babelpr.LeagueOfLegends.KassadinSummoner import KassadinSummoner
from babelpr.LeagueOfLegends.Summoner import SummonerProfileLoadFailure, \
    UnknownSummoner
from babelpr.LeagueOfLegends.SummonerMatchStats import SummonerMatchStats
from babelpr.chatbot import ChatBot
from babelpr.commands import ExplicitCommand

class DivisionCommand(ExplicitCommand):
    
    def __init__(self, chatbot):
        ExplicitCommand.__init__(self, chatbot)
        
        self.triggers = ['division']
        self.name = 'division'
        self.description = "Tells you info about the division a summoner is in"
        self.syntax = "#division SUMMONERNAME"
    
    def processCommand(self, message, trigger, arguments):
        assert isinstance(message, Message.Message)
        #assert isinstance(self._chatbot, ChatBot)
        
        arg_parts = arguments.split(' ', 1)
        if len(arg_parts) != 1:
            return "Invalid syntax.  Usage: %s" % self.syntax
        
        try:
            summoner = KassadinSummoner(arguments)
            division = summoner.getDivision()
        except UnknownSummoner:
            return "Unknown summoner: '%s'" % arguments
        except SummonerProfileLoadFailure:
            return "Failed to load summoner profile for '%s'" % arguments
        #except:
        #    return "Error while attempting to load summoner '%s'" % arguments
            
        if division is None:
            if summoner is not None and len(summoner.summoner_name) > 0:
                n = summoner.summoner_name
            else:
                n = arguments
            return "No division for '%s' found" % n

        return "%s is in %s " % (summoner.summoner_name, division)
            
        
    