class UnknownSummoner(Exception): pass
class SummonerProfileLoadFailure(Exception): pass

class Summoner(object):
    
    def __init__(self, summoner_name):
        self.summoner_name = summoner_name
    
    def getLastMatch(self):
        return None
    
    def getDivision(self):
        return None
