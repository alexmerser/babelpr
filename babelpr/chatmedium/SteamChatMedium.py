from babelpr import steamapi
from babelpr.Message import Message
from babelpr.chatmedium import AbstractChatMedium
from babelpr.logger import Logger
import time

class SteamChatMedium(AbstractChatMedium):
    
    def __init__(self, chatbot, alias, config):
        AbstractChatMedium.__init__(self, chatbot, alias, config)
        self.user = None
        self.MIN_DELAY_BETWEEN_ROSTER_CHECKS = 15
        self.last_roster = None
        self.last_roster_check_time = 0.0
    
    def start(self):
        super(SteamChatMedium, self).start()
        
        Logger.debug(self, "Starting SteamChat for '%s'" % self._alias)
        steamapi.core.APIConnection(api_key=self._config['api_key'])
        self.user = steamapi.user.SteamUser(self._config['SteamUser'])
        while True:
            time.sleep(10)
        
            
    def sendMessage(self, message):
        AbstractChatMedium.sendMessage(self, message)
        assert isinstance(message, Message)
        
    def getChannels(self):
        channels = []
        return channels
                
    def getOwnId(self):
        return self._config['SteamUser']
    
    def formatTunnelMessage(self, sender_nick, medium_alias, body):
        return AbstractChatMedium.formatTunnelMessage(self, sender_nick, medium_alias, body)
    
            
    def getRoster(self):
        t = time.time()
        
        if self.last_roster is not None and self.last_roster_check_time is not None:
            if self.last_roster_check_time + self.MIN_DELAY_BETWEEN_ROSTER_CHECKS > t:
                return self.last_roster
        
        Logger.debug(self, "Checking Steam Roster")
        roster = {}
        
        try:
            for friend in self.user.friends:

                if friend.state == 0:
                    continue
                
                roster[friend.steamid] = {
                        'name': str(friend),
                        'special': friend.currently_playing is not None,
                        'currently_playing': friend.currently_playing
                    }
        except:
            Logger.debug(self, "Exception while trying to load Steam user friends/state!")
            return self.last_roster
        
        
        self.last_roster = roster
        self.last_roster_check_time = t
        
        return roster
    
    def getRosterChanges(self):
        roster_changes = []
        new_roster = self.getRoster()
        old_roster = self._roster_changes_last_roster
        
        if old_roster is not None and new_roster is not None:
            left = []
            for player_id,data in old_roster.iteritems():
                if player_id not in new_roster and player_id not in left:
                    left.append(player_id)
                    roster_changes.append("%s signed off of %s" % (data['name'], self._alias.title()))
    
    
            joined = []
            for player_id,data in new_roster.iteritems():
                if player_id in joined:
                    continue
                if player_id not in old_roster:
                    joined.append(player_id)
                    if data['currently_playing'] is None:
                        roster_changes.append("%s logged onto %s" % (data['name'], self._alias.title()))
                    else:
                        roster_changes.append("%s logged onto %s and is playing %s" % (data['name'], self._alias.title(), data['currently_playing']))
                elif old_roster[player_id]['currently_playing'] is None and new_roster[player_id]['currently_playing'] is not None:
                    roster_changes.append("%s started playing %s on %s" % (data['name'], new_roster[player_id]['currently_playing'], self._alias.title()))
                elif old_roster[player_id]['currently_playing'] is not None and new_roster[player_id]['currently_playing'] is None:
                    roster_changes.append("%s stopped playing %s on %s" % (data['name'], old_roster[player_id]['currently_playing'], self._alias.title()))
                    
        self._roster_changes_last_roster = new_roster
        return roster_changes    
    
