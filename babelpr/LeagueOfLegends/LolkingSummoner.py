from babelpr.LeagueOfLegends.Summoner import Summoner, \
    SummonerProfileLoadFailure, UnknownSummoner
from babelpr.LeagueOfLegends.SummonerMatchStats import SummonerMatchStats
from babelpr.utils import stripHTML
import re
import urllib
import urllib2
from babelpr.LeagueOfLegends.SummonerChampionRankedStats import SummonerChampionRankedStats

class LolkingSummoner(Summoner):
    
    lastmatch_pattern = '"\/champions\/(?P<champion>[^"]+)"' + '.*' + \
        '<div style="font-size: 12px; font-weight: bold;">(?P<game_type>[^<]+)</div>' + '.*' + \
        '<div style="font-weight: bold; font-size: 16px; color: #......;">(?P<win_or_loss>[^<]+)<\/div>' + '.*' + \
        '<span style="border-bottom:[^>]+>(?P<how_long_ago>[^<]+)</span>' +  '.*' + \
        '<strong>(?P<game_length>[^\n]+)<\/strong>[^<]+<div class="match_details_cell_label">Game Length<\/div>' + '.*' + \
        '<strong>(?P<kills>\d+)</strong> <[^>]+>Kills' +  '.*' + \
        '<strong>(?P<deaths>\d+)</strong> <[^>]+>Deaths' +  '.*' + \
        '<strong>(?P<assists>\d+)</strong> <[^>]+>Assists' +  '.*' + \
        '<strong>(?P<gold>[^<]+)<\/strong><div class="match_details_cell_label">Gold<\/div>' + '.*' + \
        '<strong>(?P<cs>[^<]+)<\/strong><div class="match_details_cell_label">Minions<\/div>'                  
    lastmatch_re = re.compile(lastmatch_pattern,re.MULTILINE|re.DOTALL)
    
    ranked_champ_stats_pattern = '<tr>.*?' + \
        '<a href="/champions/[^"]+?">(?P<champion>[^<]+?)</a></div>.*?' + \
        '<td[^>]*?>(?P<wins>[^<]+?)</td>.*?' + \
        '<td[^>]*?>(?P<losses>[^<]+?)</td>.*?' + \
        '<td[^>]*?>(?P<kills>[^<]+?)/game</td>.*?' + \
        '<td[^>]*?>(?P<deaths>[^<]+?)/game</td>.*?' + \
        '<td[^>]*?>(?P<assists>[^<]+?)/game</td>.*?' + \
        '<td[^>]*?>(?P<creeps>[^<]+?)/game</td>.*?' + \
        '</tr>'
    
    division_pattern = '<div class="personal_ratings_heading">Solo 5v5</div>.*?<div class="personal_ratings_rating" [^>]+>(?P<metal>[^<]+)<[^>]+>(?P<tier>[^<]+).+?>(?P<lp>\d+) League Points'
    division_re = re.compile(division_pattern,re.MULTILINE|re.DOTALL)
    
    summoner_profile_id_cache = {}
    
    def __init__(self, summoner_name, chatbot):
        self._profile_id = None
        self._profile_html = None
        Summoner.__init__(self, summoner_name, chatbot)
        
    def getDivision(self):
        self.fetchProfile()
        r = self.division_re.search(self._profile_html)
        
        if not r:
            return None
        
        d = r.groupdict()
        return "%s %s (%s LP)" % (d['metal'], d['tier'], d['lp'])
                
    def getRankedChampionStats(self, champion_name):
        self.fetchProfile()
        
        
        topparts = self._profile_html.split('<!-- RANKED STATS -->', 1)
        if len(topparts) == 1:
            return None
        
        botparts = topparts[1].split('<!-- MATCH HISTORY -->', 1)
        if len(botparts) == 1:
            return None
        
        ranked_stats_html = botparts[0]
        
        champ_stats = SummonerChampionRankedStats('lolking', self._summoner_name, champion_name, None, None, None, None, None, None)
        champion_name_search = champion_name.lower()
        
        for m in re.finditer(self.ranked_champ_stats_pattern, ranked_stats_html, re.MULTILINE|re.DOTALL):
            d = m.groupdict(); 
            if not champion_name_search in d['champion'].lower():
                continue
            
            champion_name = d['champion'].title()
            wins = d['wins']
            losses = d['losses']
            kills = d['kills']
            deaths = d['deaths']
            assists = d['assists']
            creeps = d['creeps']
            
            champ_stats = SummonerChampionRankedStats('lolking', self._summoner_name, champion_name, wins, losses, kills, deaths, assists, creeps)
            
            break
        
        return champ_stats
    
    def getLastMatch(self, skip_num=0):
        self.fetchProfile()
        
        split_matches = self._profile_html.split('<div class="match_details">')
        if len(split_matches) == 1:
            return None
        
        match_html = split_matches[1+skip_num]
        r = self.lastmatch_re.search(match_html)
        
        if not r:
            return None
        
        d = r.groupdict()
        champion_name = d['champion'].title()
        win = d['win_or_loss'] == 'Win'
        game_type = d['game_type']
        kills = d['kills']
        deaths = d['deaths']
        assists = d['assists']
        cs = d['cs']
        gold = d['gold']
        duration = stripHTML(d['game_length'])
        how_long_ago = d['how_long_ago']
        
        matchstats = SummonerMatchStats('lolking', self._summoner_name, champion_name, win, game_type, kills, deaths, assists, cs, gold, duration, how_long_ago)
        
        return matchstats
    
    
    def fetchProfile(self):
        if self._profile_html is not None:
            return
        
        if self._profile_id is None:
            self._profile_id = self.getProfileId(self._summoner_name)
            
        if self._profile_id is None:
            return
        
        if self._profile_html is None:
            self._profile_html = self.getProfileHtml(self._profile_id)
    
    def getProfileId(self, summoner_name):
        if LolkingSummoner.summoner_profile_id_cache.has_key(summoner_name):
            return LolkingSummoner.summoner_profile_id_cache[summoner_name]
        
        opener = urllib2.build_opener()
        opener.addheaders.append(('Cookie', 'enabled-search-regions=na'))
        try:
            f = opener.open("http://www.lolking.net/search?%s" % urllib.urlencode({'name': summoner_name}), None, 5)
        except:
            raise UnknownSummoner
        
        if not f:
            raise UnknownSummoner

        fetched_url = f.geturl()
        
        if "http://www.lolking.net/summoner/na/" not in fetched_url:
            f.close()
            raise UnknownSummoner
        
        profile_id = fetched_url[35:]
        
        html = f.read()
        f.close()
        
        if self.isValidProfilePage(html):
            self._profile_html = html
        
        LolkingSummoner.summoner_profile_id_cache[summoner_name] = profile_id
        return profile_id
    
    def getProfileHtml(self, profile_id):
        opener = urllib2.build_opener()
        opener.addheaders.append(('Cookie', 'enabled-search-regions=na'))
        f = opener.open("http://www.lolking.net/summoner/na/%s" % profile_id, None, 5)
        
        if not f:       
            raise SummonerProfileLoadFailure
        
        html = f.read()
        f.close()
        
        if not self.isValidProfilePage(html):
            raise SummonerProfileLoadFailure
        
        return html
        
    def isValidProfilePage(self, html):
        pattern = '<div id="summoner-titlebar-summoner-name">(?P<summoner_name>[^<]+)</div>'
        profile_re = re.compile(pattern)
        match = profile_re.search(html)
        if not match:
            return False
        
        self._summoner_name = match.groupdict()['summoner_name']
        
        return True
        