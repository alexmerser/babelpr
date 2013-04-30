from babelpr.LeagueOfLegends.Summoner import Summoner, \
    SummonerProfileLoadFailure, UnknownSummoner
from babelpr.LeagueOfLegends.SummonerMatchStats import SummonerMatchStats
from babelpr.utils import getWebpage
from dateutil.parser import parse
import collections
import json
import pytz
import re
import urllib

class KassadinSummoner(Summoner):
    lastmatch_pattern = '<tr class="match_history_row.*?' + \
                        "<strong class='col_[^']+?'>(?P<win_or_loss>[^<]+?)</strong>.*?" + \
                        '<td class="m_datetime"[^>]+?>[^<]+?' + \
                        '<strong>(?P<map_and_queue>[^<]+?)</strong>[^<]+?' + \
                        '<br>as <strong>(?P<champion>[^<]+?)</strong>[^<]+?' + \
                        '<br>(?P<match_time>[^-]+?)-0700.*?' + \
                        '<td class="m_kda centre">[^<]+?<span class="p_large0">(?P<kda>[^<]+?)</span>.*?' + \
                        '"Total minion kills">=(?P<cs>[^<]+?)</abbr>t.*?' + \
                        '<td class="m_gold centre">[^<]+?<span class="p_large0">(?P<gold>[^<]+?)</span>.*?' + \
                        '</tr>.*'
    lastmatch_re = re.compile(lastmatch_pattern,re.MULTILINE|re.DOTALL)    
    
    pbk_pattern = 'name="PBK" value="(?P<pbk>[^"]+)"'            
    pbk_re = re.compile(pbk_pattern,re.MULTILINE|re.DOTALL)    
    
    def __init__(self, summoner_name):
        p = self.fetchProfile(summoner_name)
        if p is None:
            raise UnknownSummoner
        self.summoner_name = p.summoner_name
        self._pbk = p.pbk
        
        Summoner.__init__(self, p.summoner_name)
    
    def getDivision(self):
        season_url = "http://quickfind.kassad.in/lookup/season3?PBK=%s&regionProxy=na&summoner=%s" % (self._pbk, self.summoner_name)
        season_json = getWebpage(season_url)
        try:
            season_data = json.loads(season_json)
        except:
            return None
        
        division = season_data['right'].split('<br> ')[1]
        lp = ''
        
        if " LP," in season_data['left']:
            lp = " (%s LP)" % season_data['left'].split(' LP,')[0]
        
        
        return division+lp
    
    def getLastMatch(self):
        match_url = "http://quickfind.kassad.in/lookup/match?PBK=%s&regionProxy=na&summoner=%s" % (self._pbk, self.summoner_name)
        match_json = getWebpage(match_url)
        try:
            match_data = json.loads(match_json)
        except:
            return None
        match_html = match_data['escaped_html']
        
        
        r = [m.groupdict() for m in self.lastmatch_re.finditer(match_html)]
        
        if not r or len(r) == 0:
            return None
        
        d = r[0]
        champion_name = d['champion']
        win = d['win_or_loss'] == 'WIN'
        game_type = d['map_and_queue']
        how_long_ago = self.pretty_date(parse(d['match_time'] + '-0700'))
        
        kda = d['kda'].split("/")
        
        kills = kda[0]
        deaths = kda[1]
        assists = kda[2]
        cs = d['cs']
        gold = d['gold']
        duration = None
        
        
        matchstats = SummonerMatchStats(self.summoner_name, champion_name, win, game_type, kills, deaths, assists, cs, gold, duration, how_long_ago)
        return matchstats        
    
    def pretty_date(self, time=False):
        """
        Get a datetime object or a int() Epoch timestamp and return a
        pretty string like 'an hour ago', 'Yesterday', '3 months ago',
        'just now', etc
        """
        from datetime import datetime
        now = datetime.now(pytz.utc)
        if type(time) is int:
            diff = now - datetime.fromtimestamp(time)
        elif isinstance(time,datetime):
            diff = now - time 
        elif not time:
            diff = now - now
        second_diff = diff.seconds
        day_diff = diff.days
    
        if day_diff < 0:
            return ''
    
        if day_diff == 0:
            if second_diff < 10:
                return "just now"
            if second_diff < 60:
                return str(second_diff) + " seconds ago"
            if second_diff < 120:
                return  "a minute ago"
            if second_diff < 3600:
                return str( second_diff / 60 ) + " minutes ago"
            if second_diff < 7200:
                return "an hour ago"
            if second_diff < 86400:
                return str( second_diff / 3600 ) + " hours ago"
        if day_diff == 1:
            return "Yesterday"
        if day_diff < 7:
            return str(day_diff) + " days ago"
        if day_diff < 31:
            return str(day_diff/7) + " weeks ago"
        if day_diff < 365:
            return str(day_diff/30) + " months ago"
        return str(day_diff/365) + " years ago"    
    
    def fetchProfile(self, search_name):
        search_url = "http://quickfind.kassad.in/profile/na/%s/" % urllib.quote(search_name)
        search_html = getWebpage(search_url)
        
        r = self.pbk_re.search(search_html)
        
        if not r:
            return None
        
        d = r.groupdict()
        pbk = d['pbk']
        
        lookup_url = "http://quickfind.kassad.in/lookup?PBK=%s&regionProxy=na&summoner=%s" % (pbk, search_name)
        lookup_json = getWebpage(lookup_url)
        try:
            lookup_data = json.loads(lookup_json)
        except:
            return None
        summoner_name = lookup_data['name']
        
        response = collections.namedtuple('Response', ['summoner_name', 'pbk'])
        return response(summoner_name, pbk)
    
    def isValidProfilePage(self, html):
        return True
