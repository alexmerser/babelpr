from babelpr import Message
from babelpr.LeagueOfLegends.KassadinSummoner import KassadinSummoner
from babelpr.LeagueOfLegends.LolkingSummoner import LolkingSummoner
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
        
        arguments = arguments.strip()
        if len(arguments) == 0:
            return "Invalid syntax.  Usage: %s" % self.syntax
        
        division = None
        try:
            summoner = LolkingSummoner(arguments)
            division = summoner.getDivision()
        except:
            division = None
            
        if division is None:
            try:
                summoner = KassadinSummoner(arguments)
                division = summoner.getDivision()
            except:
                division = None
            

        if division is None:
            return "Unable to load/find division information for '%s'" % arguments
            
        return "%s is in %s " % (summoner.summoner_name, division)
            
        
    