class UnknownSummoner(Exception): pass
class SummonerProfileLoadFailure(Exception): pass

class Summoner(object):
    
    def __init__(self, summoner_name, chatbot):
        self._summoner_name = summoner_name
        self._chatbot = chatbot
    
    def getLastMatch(self):
        return None
    
    def getDivision(self):
        return None

    def getSummonerName(self):
        return self._summoner_name