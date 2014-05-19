from babelpr.LeagueOfLegends.Summoner import Summoner, UnknownSummoner
from babelpr.LeagueOfLegends.SummonerMatchStats import SummonerMatchStats
from babelpr.utils import PrettyRelativeTime, getWebpage
import re, urllib, time, logging

class OpggSummoner(Summoner):

    lastmatch_pattern = '<div class="subType">(?P<queue_type>.*?)<span class="premadeSize">(?P<premade_size>[^<]+)</span>' + '.*' + \
        "data-datetime='(?P<match_time>\d+)" + '.*' + \
        '<span class="gameResult">(?P<win_or_loss>.*?\s*?</span>.*?\s*?)</span>' + '.*' + \
        '<div class="championName">(?P<champion>[^<]+)</div>' + '.*' + \
        '<span class="kill">(?P<kills>\d+)</span>' + '.*' + \
        '<span class="death">(?P<deaths>\d+)</span>' + '.*' + \
        '<span class="assist">(?P<assists>\d+)</span>' + '.*' + \
        '<span class="cs">(?P<cs>\d+)[^<]*?</span>' + '.*' + \
        '<span class="gold">(?P<gold>[^<]+)</span>'
    lastmatch_re = re.compile(lastmatch_pattern,re.MULTILINE|re.DOTALL)
    
    
    division_pattern = '<span class="tierRank">(?P<tierRank>[^<]+)</span>.*?<span class="leaguePoints">(?P<lp>\d+) LP</span>'
    division_re = re.compile(division_pattern,re.MULTILINE|re.DOTALL)
    
    summoner_id_cache = {}
    
    def __init__(self, summoner_name, chatbot):
        logging.info("Constructing OpggSummoner")
        self._summoner_id = None
        self._profile_html = None
        Summoner.__init__(self, summoner_name, chatbot)
        
    def getDivision(self):
        self.fetchProfile()
        r = self.division_re.search(self._profile_html)
        
        if not r:
            logging.info("No division re pattern match found in op.gg profile HTML")
            return None
        
        d = r.groupdict()
        return "%s (%s LP)" % (d['tierRank'], d['lp'])
                
    def getRankedChampionStats(self, champion_name):
        raise UnknownSummoner
    
    def getLastMatch(self, skip_num=0):
        logging.info("Getting LastMatch via OpggSummoner")
        self.fetchProfile()
        
        split_matches = self._profile_html.split('<div class="GameBox ')
        if len(split_matches) == 1:
            logging.info("No GameBox found in op.gg profile HTML")
            return None
        
        match_html = split_matches[1+skip_num]
        r = self.lastmatch_re.search(match_html)

        if not r:
            logging.info("No LastMatch re patterm match found in op.gg profile HTML")
            return None
        
        d = r.groupdict()
        champion_name = d['champion'].title()
        win = 'Victory' in d['win_or_loss']
        game_type = "%s (%s)" % (d['queue_type'].strip('- ').strip(), d['premade_size'])
        kills = d['kills']
        deaths = d['deaths']
        assists = d['assists']
        cs = d['cs']
        gold = d['gold'] + " gold"
        duration = "Unknown"

        match_time = int(d['match_time'])
        how_long_ago = PrettyRelativeTime(time.time() - match_time)
        
        matchstats = SummonerMatchStats('opgg', self._summoner_name, champion_name, win, game_type, kills, deaths, assists, cs, gold, duration, how_long_ago)
        
        return matchstats
    
    
    def fetchProfile(self):
        if self._profile_html is not None:
            return
        
        if self._summoner_id is None:
            self._summoner_name, self._summoner_id = self.getSummonerNameAndId(self._summoner_name)
            
        if self._summoner_id is None:
            return
        
        if self._profile_html is None:
            self._profile_html = self.getProfileHtml(self._summoner_id, self._summoner_name)

    def getProfileUrl(self, summoner_name):
        return "http://na.op.gg/summoner/%s" % urllib.urlencode({'userName': summoner_name})
    
    def getSummonerNameAndId(self, summoner_name):
        if OpggSummoner.summoner_id_cache.has_key(summoner_name):
            return summoner_name, OpggSummoner.summoner_id_cache[summoner_name]
        
        html = getWebpage(self.getProfileUrl(summoner_name))
        summoner_name, summoner_id = self.getNameAndIdFromProfile(html)
        OpggSummoner.summoner_id_cache[summoner_name] = summoner_id

        return summoner_name, summoner_id
    
    def getProfileHtml(self, summoner_id, summoner_name):
        #refresh the profile
        getWebpage("http://na.op.gg/summoner/ajax/update.json/summonerId="+summoner_id)

        #fetch the refreshed profile
        html = getWebpage(self.getProfileUrl(summoner_name))
        
        # for validation
        self.getNameAndIdFromProfile(html)
        
        return html
        
    def getNameAndIdFromProfile(self, html):
        # extract summoner name
        pattern = '<span class="summonerName">(?P<summoner_name>[^<]+)</span>'
        profile_re = re.compile(pattern)
        match = profile_re.search(html)
        if not match:
            logging.info("No summoner name found in op.gg profile HTML")
            raise UnknownSummoner
        
        summoner_name = match.groupdict()['summoner_name']


        # extract summoner id
        pattern = 'data-summoner-id="(?P<summoner_id>\d+)"'
        profile_re = re.compile(pattern)
        match = profile_re.search(html)
        if not match:
            logging.info("No summoner id found in op.gg profile HTML")
            raise UnknownSummoner

        summoner_id = match.groupdict()['summoner_id']
        
        return summoner_name, summoner_id
        