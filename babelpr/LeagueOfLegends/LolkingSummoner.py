from babelpr.LeagueOfLegends.Summoner import Summoner,\
    SummonerProfileLoadFailure, UnknownSummoner
import urllib2
import urllib
import re
from babelpr.LeagueOfLegends.SummonerMatchStats import SummonerMatchStats

class LolkingSummoner(Summoner):
    
    lastmatch_pattern = '"\/champions\/(?P<champion>[^"]+)"' + '.*' + \
        '<div style="font-size: 12px; font-weight: bold;">(?P<game_type>[^<]+)</div>' + '.*' + \
        '<div style="font-weight: bold; font-size: 16px; color: #......;">(?P<win_or_loss>[^<]+)<\/div>' + '.*' + \
        '<span style="border-bottom:[^>]+>(?P<how_long_ago>[^<]+)</span>' +  '.*' + \
        '<strong>(?P<game_length>[^<]+)<\/strong>[^<]+<div class="match_details_cell_label">Game Length<\/div>' + '.*' + \
        '<strong>(?P<kills>\d+)</strong> <[^>]+>Kills' +  '.*' + \
        '<strong>(?P<deaths>\d+)</strong> <[^>]+>Deaths' +  '.*' + \
        '<strong>(?P<assists>\d+)</strong> <[^>]+>Assists' +  '.*' + \
        '<strong>(?P<gold>[^<]+)<\/strong><div class="match_details_cell_label">Gold<\/div>' + '.*' + \
        '<strong>(?P<cs>[^<]+)<\/strong><div class="match_details_cell_label">Minions<\/div>'                  
    lastmatch_re = re.compile(lastmatch_pattern,re.MULTILINE|re.DOTALL)
    

    elo_pattern = '<li.*?' +\
        '<div class="personal_ratings_heading">(?P<rating_type>[^<]+)<\/div>.*?' + \
        '<div class="personal_ratings_rating">(?P<max_elo>[^<]+)</div>.*?' + \
        '(<span [^>]+>(?P<wins>[^<]+)</span> Wins</div>.*?)?' + \
        '(<span [^>]+>(?P<losses>[^<]+)</span> Losses</div>.*?)?' + \
        '(<span [^>]+>(?P<current_elo>[^<]+)</span> Rating</div>.*?)?' + \
        '<\/li'            
    elo_re = re.compile(elo_pattern,re.MULTILINE|re.DOTALL)
    
    
    summoner_profile_id_cache = {}
    
    _profile_id = None
    _profile_html = None
    _elos = None
    
    _ranked_games = {
        '5V5_TEAM': {'wins': None, 'losses': None},
        '5V5_SOLO': {'wins': None, 'losses': None},
        '3V3_TEAM': {'wins': None, 'losses': None}
    }
    
    def getLastMatch(self):
        self.fetchProfile()
        
        topparts = self._profile_html.split('<!-- MATCH HISTORY -->', 1)
        if len(topparts) == 1:
            return None
        
        
        matches = topparts[1].split('<!-- MASTERIES -->', 1)[0]
        split_matches = matches.split('<div class="match_details">')
        if len(split_matches) == 1:
            return None
        
        match_html = split_matches[1]
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
        duration = d['game_length']
        how_long_ago = d['how_long_ago']
        
        matchstats = SummonerMatchStats(self.summoner_name, champion_name, win, game_type, kills, deaths, assists, cs, gold, duration, how_long_ago)
        
        return matchstats
    
    def getElo(self, elo_type):
        elos = self.getElos()
        if elo_type in elos:
            return elos[elo_type]
        
        return None
    
    def getWinsLosses(self, queue_type):
        self.getElos()
        queue_type = queue_type.upper()
        if(self._ranked_games.has_key(queue_type)):
            return self._ranked_games[queue_type]
        return {'wins': None, 'losses': None} 

    def getElos(self):
        self.fetchProfile()
        
        if(self._elos is not None):
            return self._elos
        
        elos = {}
        for elo_type, type_id in self.ELO_TYPES.iteritems():
            elos[elo_type] = None
                    
        for elo_match in [m.groupdict() for m in self.elo_re.finditer(self._profile_html)]:
            if elo_match['rating_type'] == 'Team 3v3':
                elos['ELO_3V3_TEAM_MAX'] = elo_match['max_elo']
                elos['ELO_3V3_TEAM_CURRENT'] = elo_match['current_elo']
                self._ranked_games['3V3_TEAM']['wins'] = elo_match['wins']
                self._ranked_games['3V3_TEAM']['losses'] = elo_match['losses']
            elif elo_match['rating_type'] == 'Team 5v5':
                elos['ELO_5V5_TEAM_MAX'] = elo_match['max_elo']
                elos['ELO_5V5_TEAM_CURRENT'] = elo_match['current_elo']
                self._ranked_games['5V5_TEAM']['wins'] = elo_match['wins']
                self._ranked_games['5V5_TEAM']['losses'] = elo_match['losses']
            elif elo_match['rating_type'] == 'Solo 5v5':
                elos['ELO_5V5_SOLO_MAX'] = elo_match['max_elo']
                elos['ELO_5V5_SOLO_CURRENT'] = elo_match['current_elo']
                self._ranked_games['5V5_SOLO']['wins'] = elo_match['wins']
                self._ranked_games['5V5_SOLO']['losses'] = elo_match['losses']
        
        self._elos = elos
        
        return elos
    
    def fetchProfile(self):
        if self._profile_html is not None:
            return
        
        if self._profile_id is None:
            self._profile_id = self.getProfileId(self.summoner_name)
            
        if self._profile_id is None:
            return
        
        if self._profile_html is None:
            self._profile_html = self.getProfileHtml(self._profile_id)
    
    def getProfileId(self, summoner_name):
        if LolkingSummoner.summoner_profile_id_cache.has_key(summoner_name):
            return LolkingSummoner.summoner_profile_id_cache[summoner_name]
        
        opener = urllib2.build_opener()
        opener.addheaders.append(('Cookie', 'enabled-search-regions=na'))
        f = opener.open("http://www.lolking.net/search?%s" % urllib.urlencode({'name': summoner_name}), None, 5)
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
        pattern = '<div style="font-size: 36px; line-height: 44px; white-space: nowrap;">(?P<summoner_name>[^<]+)</div>'
        profile_re = re.compile(pattern)
        match = profile_re.search(html)
        if not match:
            return False
        
        self.summoner_name = match.groupdict()['summoner_name']
        
        return True
        