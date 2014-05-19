from babelpr.LeagueOfLegends.Summoner import Summoner, UnknownSummoner
from babelpr.LeagueOfLegends.SummonerMatchStats import SummonerMatchStats
from babelpr.utils import performRestApiGet, PrettyRelativeTime
import urllib, logging, time

class RiotApiSummoner(Summoner):

    summoner_id_cache = {}
    chamption_name_cache = {}
    
    def __init__(self, summoner_name, chatbot):
        logging.info("Constructing RiotApiSummoner")
        self._summoner_id = None
        self._recent_games = None
        Summoner.__init__(self, summoner_name, chatbot)
        
    def getDivision(self):
        sid = str(self.getSummonerId())
        le = self.getLeagueEntries()

        tier = None
        lp = None
        for queue in le[sid]:
            print queue['queue']
            if queue['queue'] == 'RANKED_SOLO_5x5':
                tier = queue['tier'].capitalize() + " " + queue['entries'][0]['division']
                lp = queue['entries'][0]['leaguePoints']
                break

        if tier is None or lp is None:
            raise UnknownSummoner

        return "%s (%s LP)" % (tier, lp)
                
    def getRankedChampionStats(self, champion_name):
        raise UnknownSummoner
    
    def getLastMatch(self, skip_num=0):
        rgo = self.getRecentGames()
        
        games = rgo['games']
        if len(games) < skip_num + 1:
            return None

        game = games[skip_num]
        matchstats = SummonerMatchStats(
            'riotapi', 
            self._summoner_name, 
            self.getChampionName(game['championId']), 
            game['stats']['win'], 
            self.getFriendlyGameType(game), 
            game['stats']['championsKilled'], 
            game['stats']['numDeaths'], 
            game['stats']['assists'], 
            game['stats']['minionsKilled']+game['stats']['neutralMinionsKilled'], 
            self.getFriendlyGoldAmount(game['stats']['goldEarned']), 
            self.getFriendlyDuration(game['stats']['timePlayed']), 
            self.getFriendlyTimeAgo(game['createDate'])
        )
        
        return matchstats

    def getChampionName(self, championId):
        championId = str(championId)
        if not RiotApiSummoner.chamption_name_cache.has_key(championId):
            key = self.getApiKey()
            endpoint = "https://prod.api.pvp.net/api/lol/static-data/na/v1.2/champion/%s?api_key=%s" % (urllib.quote_plus(championId), key)
            response_code, response_object = performRestApiGet(endpoint)
            if(response_code != 200):
                return "Unknown"

            RiotApiSummoner.chamption_name_cache[championId] = response_object['name']

        return RiotApiSummoner.chamption_name_cache[championId]

    def getFriendlyTimeAgo(self, createDate):
        return PrettyRelativeTime(time.time() - createDate/1000) + " ago"

    def getFriendlyGameType(self, game):
        return game['subType'].replace('_', ' ').title()

    def getFriendlyDuration(self, timePlayed):
        mins = int(timePlayed / 60)
        return "%s mins" % mins

    def getFriendlyGoldAmount(self, gold):
        if gold < 1000:
            gold_str = str(gold)
        else:
            gold_str = "%sk" % round(gold / 1000.0,1)

        return gold_str + " gold"

    def getApiKey(self):
        return self._chatbot._config['riot_api_key']

    def getSummonerId(self):
        if RiotApiSummoner.summoner_id_cache.has_key(self._summoner_name):
            return RiotApiSummoner.summoner_id_cache[self._summoner_name]

        if self._summoner_id is None:
            key = self.getApiKey()
            endpoint = "https://prod.api.pvp.net/api/lol/na/v1.4/summoner/by-name/%s?api_key=%s" % (urllib.quote_plus(self._summoner_name), key)
            response_code, response_object = performRestApiGet(endpoint)
            if(response_code != 200):
                raise UnknownSummoner

            self._summoner_id = response_object[self._summoner_name]["id"]
            self._summoner_name = response_object[self._summoner_name]["name"]

        RiotApiSummoner.summoner_id_cache[self._summoner_name] = self._summoner_id
        return self._summoner_id
    
    def getRecentGames(self):
        key = self.getApiKey()
        summoner_id = self.getSummonerId()
        endpoint = "https://prod.api.pvp.net/api/lol/na/v1.3/game/by-summoner/%s/recent?api_key=%s" % (summoner_id, key)
        response_code, response_object = performRestApiGet(endpoint)
        if(response_code != 200):
            raise UnknownSummoner

        return response_object

    def getLeagueEntries(self):
        key = self.getApiKey()
        summoner_id = self.getSummonerId()
        endpoint = "https://prod.api.pvp.net/api/lol/na/v2.4/league/by-summoner/%s/entry?api_key=%s" % (summoner_id, key)
        response_code, response_object = performRestApiGet(endpoint)
        if(response_code != 200):
            raise UnknownSummoner

        return response_object
