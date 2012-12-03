class SummonerMatchStats(object):
    summoner_name = None
    champion = None
    win = None
    game_type = None
    kills = None
    deaths = None
    assists = None
    cs = None
    gold = None
    duration = None
    how_long_ago = None
    
    def __init__(self, summoner_name, champion, win, game_type, kills, deaths, assists, cs, gold, duration, how_long_ago):
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
        self.how_long_ago = how_long_ago        

    def toString(self):
        if self.kills is None:
            return "Unknown"
        
        message = ("%(summoner_name)s: %(victory_text)s a %(game_type)s in %(duration)s %(how_long_ago)s as %(champion)s. K/D/A was %(kills)s/%(deaths)s/%(assists)s with %(cs)s CS and %(gold)s gold.") % {
            'summoner_name': self.summoner_name,
            'champion': self.champion,
            'how_long_ago': self.how_long_ago,
            'game_type': self.game_type,
            'kills': self.kills,
            'deaths': self.deaths,
            'assists': self.assists,
            'cs': self.cs,
            'gold': self.gold,
            'victory_text': "won" if self.win else "lost",
            'duration': self.duration
        }
        
        return message
    