from babelpr import Message
from babelpr.LeagueOfLegends.KassadinSummoner import KassadinSummoner
from babelpr.LeagueOfLegends.Summoner import SummonerProfileLoadFailure, \
    UnknownSummoner
from babelpr.LeagueOfLegends.SummonerMatchStats import SummonerMatchStats
from babelpr.chatbot import ChatBot
from babelpr.commands import ExplicitCommand

class LastCommand(ExplicitCommand):
    
    def __init__(self, chatbot):
        ExplicitCommand.__init__(self, chatbot)
        
        self.triggers = ['last']
        self.name = 'last'
        self.description = "Tells you info about the last game a summoner played"
        self.syntax = "#last SUMMONERNAME"
    
    def processCommand(self, message, trigger, arguments):
        assert isinstance(message, Message.Message)
        #assert isinstance(self._chatbot, ChatBot)
        
        arg_parts = arguments.split(' ', 1)
        if len(arg_parts) != 1:
            return "Invalid syntax.  Usage: %s" % self.syntax
        
        try:
            summoner = KassadinSummoner(arguments)
            last_match = summoner.getLastMatch()
        except UnknownSummoner:
            return "Unknown summoner: '%s'" % arguments
        except SummonerProfileLoadFailure:
            return "Failed to load summoner profile for '%s'" % arguments
        #except:
        #    return "Error while attempting to load summoner '%s'" % arguments
            
        if last_match is None:
            return "No recent matches for '%s' found" % arguments

        assert isinstance(last_match, SummonerMatchStats)
        
        return last_match.toString()
            
        
    