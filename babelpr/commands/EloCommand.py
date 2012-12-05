from babelpr.commands import TriggeredCommand
from babelpr import Message
from babelpr.chatbot import ChatBot
from babelpr.LeagueOfLegends.Summoner import SummonerProfileLoadFailure,\
    UnknownSummoner, Summoner
from babelpr.LeagueOfLegends.LolkingSummoner import LolkingSummoner

class EloCommand(TriggeredCommand):
    triggers = ['elo']
    name = 'elo'
    description = "Fetches the elo for a given summoner"
    syntax = "#elo [5v5_solo|5v5_team|3v3_team] summoner"

    def processCommand(self, message, trigger, arguments):
        assert isinstance(message, Message.Message)
        assert isinstance(self._chatbot, ChatBot)
        
        arg_parts = arguments.split(' ', 1)
        if len(arg_parts) == 1:
            elo_type = '5V5_SOLO'
            summoner_name = arg_parts[0]
        else:
            elo_type = arg_parts[0].upper()
            summoner_name = arg_parts[1]
            
        if elo_type == '5V5' or elo_type == '5V5SOLO' or elo_type == '5' or elo_type == 'SOLO':
            elo_type = '5V5_SOLO'
        
        if elo_type == '5V5TEAM' or elo_type == '5S':
            elo_type = '5V5_SOLO'
        
        if elo_type == '3V3' or elo_type == '3V3TEAM' or elo_type == '3' or elo_type == '3S':
            elo_type = '3V3_TEAM'
            
        current_key = 'ELO_%s_CURRENT' % elo_type
        max_key = 'ELO_%s_MAX' % elo_type
        if not Summoner.ELO_TYPES.has_key(current_key):
            return "Invalid syntax.  Usage: %s" % self.syntax

        try:
            summoner = LolkingSummoner(summoner_name)
            elos = summoner.getElos()
        except UnknownSummoner:
            return "Unknown summoner: '%s'" % summoner_name
        except SummonerProfileLoadFailure:
            return "Failed to load summoner profile for '%s'" % summoner_name
        #except:
        #    return "Error while attempting to load summoner '%s'" % summoner
        
        wins_losses = summoner.getWinsLosses(elo_type)
        if(wins_losses['wins'] is not None and wins_losses['losses'] is not None):
            win_loss_str = ". %s wins, %s losses" % (wins_losses['wins'], wins_losses['losses'])
            nogames = wins_losses['wins'] == '0' and wins_losses['losses'] == '0'
        else:
            win_loss_str = ''
            nogames = False
        
        friendly_elo_type = elo_type.lower().replace('_', ' ')
        
        if elos[max_key] == 'Unranked' and nogames:
            return "%s is bad at %s (unranked)" % (summoner.summoner_name, friendly_elo_type)
            
        if elos[max_key] is None or elos[max_key] == 'Unranked':
            return "%s is unranked for %s%s" % (summoner.summoner_name, friendly_elo_type, win_loss_str)
        
        if elos[current_key] is None:
            return "%s's max %s elo is %s (but currently under 1200)%s" % (summoner.summoner_name, friendly_elo_type, elos[max_key], win_loss_str)
        
        return "%s's max %s elo is %s, currently %s%s" % (summoner.summoner_name, friendly_elo_type, elos[max_key], elos[current_key], win_loss_str)
            
        
    