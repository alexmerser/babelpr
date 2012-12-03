class UnknownSummoner(Exception): pass
class SummonerProfileLoadFailure(Exception): pass

class Summoner(object):
    
    ELO_TYPES = {
        'ELO_5V5_SOLO_CURRENT': 1,
        'ELO_5V5_SOLO_MAX': 2,
        'ELO_3V3_TEAM_CURRENT': 3,
        'ELO_3V3_TEAM_MAX': 4,
        'ELO_5V5_TEAM_CURRENT': 5,
        'ELO_5V5_TEAM_MAX': 6
    }
    
    summoner_name = None
     
    def __init__(self, summoner_name):
        self.summoner_name = summoner_name
    
    def getLastMatch(self):
        return None
    
    def getElo(self, elo_type):
        return None
    
    def getWinsLosses(self, queue_type):
        return {'wins': None, 'losses': None} 

    def getElos(self):
        elos = {}
        for elo_type, type_id in self.ELO_TYPES.iteritems():
            elos[elo_type] = None
        return elos