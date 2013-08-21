class SummonerMatchStats(object):
    
    def __init__(self, source, summoner_name, champion, win, game_type, kills, deaths, assists, cs, gold, duration, how_long_ago):
        self.source = source
        self.summoner_name = summoner_name
        self.champion = champion
        self.win = win
        self.game_type = game_type
        self.kills = kills
        self.deaths = deaths
        self.assists = assists
        self.cs = cs
        self.gold = gold
        self.duration = duration
        if(self.duration is not None and (len(self.duration) == 0 or self.duration.lower() == "unknown")):
            self.duration = None
        self.how_long_ago = how_long_ago        

    def toString(self):
        if self.kills is None:
            return "Unknown"
        
        message = ("%(summoner_name)s%(source)s: %(victory_text)s %(game_type)s %(duration_text)s%(how_long_ago)s as %(champion)s. K/D/A was %(kills)s/%(deaths)s/%(assists)s with %(cs)s CS and %(gold)s") % {
            'summoner_name': self.summoner_name,
            'source': " (%s)" % self.source if self.source is not None else '',
            'champion': self.champion,
            'how_long_ago': self.how_long_ago,
            'game_type': self.game_type,
            'duration_text': "in %s " % self.duration if self.duration is not None else '',
            'kills': self.kills,
            'deaths': self.deaths,
            'assists': self.assists,
            'cs': self.cs,
            'gold': self.gold,
            'victory_text': "won" if self.win else "lost"
        }
        
        return message
    