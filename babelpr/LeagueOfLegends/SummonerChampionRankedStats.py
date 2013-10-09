class SummonerChampionRankedStats(object):
    
    def __init__(self, source, summoner_name, champion, wins, losses, kills, deaths, assists, creeps):
        self.source = source
        self.summoner_name = summoner_name
        self.champion = champion
        self.wins = wins
        self.losses = losses
        self.kills = kills
        self.deaths = deaths
        self.assists = assists
        self.creeps = creeps

    def toString(self):
        if self.wins is None:
            return "%(summoner_name)s doesn't seem to have played '%(champion)s' in ranked." % {
                'summoner_name': self.summoner_name,
                'champion': self.champion
            }
        
        message = ("%(summoner_name)s has played %(champion)s %(total_games)s times in ranked games. He is %(wins)s-%(losses)s with avg K/D/A of %(kills)s/%(deaths)s/%(assists)s and averages %(creeps)s minions per game.") % {
            'summoner_name': self.summoner_name,
            'champion': self.champion,
            'total_games': str(int(self.wins) + int(self.losses)),
            'wins': self.wins,
            'losses': self.losses,
            'kills': self.kills,
            'deaths': self.deaths,
            'assists': self.assists,
            'creeps': self.creeps
        }
        
        return message
    