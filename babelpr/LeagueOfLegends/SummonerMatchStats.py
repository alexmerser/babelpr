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
        
        message = ("%(summoner_name)s last played %(champion)s %(how_long_ago)s in a %(game_type)s game. " + \
        "They %(victory_text_past)s in %(duration)s " + \
        "with k/d/a of %(kills)s/%(deaths)s/%(assists)s " + \
        "and %(cs)s CS, %(gold)s gold") % {
            'summoner_name': self.summoner_name,
            'champion': self.champion,
            'how_long_ago': self.how_long_ago,
            'game_type': self.game_type,
            'kills': self.kills,
            'deaths': self.deaths,
            'assists': self.assists,
            'cs': self.cs,
            'gold': self.gold,
            'victory_text_past': "won" if self.win else "lost",
            'duration': self.duration
        }
        
        return message
    