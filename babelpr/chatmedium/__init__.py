from babelpr.logger import Logger
import re
from babelpr.Message import Message
from threading import Thread, Lock
import time
from Queue import Queue

class AbstractChatMedium(object):
    
    CHANNEL_TYPE_GROUP = 1
    CHANNEL_TYPE_INDIVIDUAL = 2
    
    def __init__(self, chatbot, alias, config):
        self._config = {}
        self._chatbot = {}
        self._isAlive = True
        self._alias = None
        self._tunnel_regex = {}
        self._message_queue = Queue()
        self._last_message_sent = time.time()
        self.MIN_DELAY_BETWEEN_MESSAGES = 0.5
        
        self._roster_changes_last_roster = None
        
        Logger.info(self, "%s %s initalizing..." % (alias, config['medium']))
        self._alias = alias
        self._config = config
        self._chatbot = chatbot
        
        Thread(target=self.processMessageQueue, args=()).start()
        
        
        if self._config.has_key('tunnels'):
            for tunnel_id,patterns in self._config['tunnels'].iteritems():
                regexs = []
                for pattern in patterns:
                    regexs.append(re.compile(pattern))
                    self._tunnel_regex[tunnel_id] = regexs
    
    def start(self):
        Logger.info(self, "%s %s starting..." % (self._alias, self._config['medium']))

    def isAlive(self):
        return self._isAlive
    
    def sendBodyToTarget(self, target_type, target, body):
        message = Message(self._alias, self.getMediumName(), target_type, target, self.getOwnId(), self.getOwnNick(), body)
        self.enqueueMessage(message)
    
    def enqueueMessage(self, message):
        self._message_queue.put(message, True)
        
    def sendMessage(self, message):
        self._last_message_sent = time.time()
        
    def getMediumName(self):
        return self._config['medium']
    
    def getUniqueIdForSender(self, message):
        assert isinstance(message, Message)
        
        if message.channel_type == self.CHANNEL_TYPE_GROUP:
            return self.getUniqueUserIdForGroupSender(message)
        
        return self.getUniqueUserIdForIndividualSender(message)
    
    def getUniqueUserIdForGroupSender(self, message):
        assert isinstance(message, Message)
        return message.sender_id
        
    def getUniqueUserIdForIndividualSender(self, message):
        assert isinstance(message, Message)
        return message.sender_id
    
    def getUserUniqueId(self, provided_nick):
        roster = self.getRoster()
        provided_nick = provided_nick.lower()
        
        # first check for an exact roster_id match
        for roster_id in roster.iterkeys():
            if roster_id.lower() == provided_nick:
                return roster_id
        
        #then check for an exact nick match
        for roster_id, roster_data in roster.iteritems():
            if roster_data['name'].lower() == provided_nick:
                return roster_id

        #then check for a partial roster_id match
        for roster_id in roster.iterkeys():
            if roster_id.lower().find(provided_nick) == 0:
                return roster_id
            
        #finally, check for a partial nick match
        for roster_id, roster_data in roster.iteritems():
            if roster_data['name'].lower().find(provided_nick) == 0:
                return roster_id
        
        return None
    
    def getRoster(self):
        return {}
    
    def getRosterChanges(self):
        roster_changes = []
        new_roster = self.getRoster()
        old_roster = self._roster_changes_last_roster
        
        if old_roster is not None and new_roster is not None:
            left = []
            for data in old_roster.itervalues():
                if data['name'] not in new_roster and data['name'] not in left:
                    left.append(data['name'])
                    roster_changes.append("%s left %s" % (data['name'], self._alias))
    
    
            joined = []
            for data in new_roster.itervalues():
                if data['name'] not in old_roster and data['name'] not in joined:
                    joined.append(data['name'])
                    roster_changes.append("%s joined %s" % (data['name'], self._alias))
                    
        self._roster_changes_last_roster = new_roster
        return roster_changes
        
    
    def getOwnId(self):
        return None
    
    def getOwnNick(self):
        return self._config['bot_nick']

    def getChannels(self):
        return []
    
    def getUserNick(self, user_id):
        roster = self.getRoster()
        
        for roster_id, roster_data in roster.iteritems():
            if roster_id == user_id:
                return roster_data['name']
            
        return user_id
    
    def getTunnelsForChannel(self, channel_id):
        matches = []
        for tunnel_id, tunnel_regexs in self._tunnel_regex.iteritems():
            for regex in tunnel_regexs:
                if regex.search(channel_id):
                    matches.append(tunnel_id)
                    break
        return matches
        
    
    def getChannelsForTunnel(self, tunnel_id):
        matches = []
        if self._tunnel_regex.has_key(tunnel_id):
            for regex in self._tunnel_regex[tunnel_id]:
                this_matches = self.getChannelsMatchingPattern(regex)
                matches = list(set(matches + this_matches))
        return matches

    def getChannelsMatchingPattern(self, regex):
        matching = []
        for channel in self.getChannels():
            if regex.search(channel):
                matching.append(channel)
        return matching
    
    def formatTunnelMessage(self, sender_nick, medium_alias, body):
        return "%s (%s): %s" % (sender_nick, medium_alias, body)
    
    def relayTunnelMessage(self, tunnel_id, source_message):
        # ignore messages from the channel itself
        if source_message.channel_id == source_message.sender_id:
            return
        
        body = self.formatTunnelMessage(source_message.sender_nick, source_message.medium_alias, source_message.body)
        channels = self.getChannelsForTunnel(tunnel_id)
        for channel in channels:
            if channel != source_message.channel_id:
                self.sendBodyToTarget(self.CHANNEL_TYPE_GROUP, channel, body)
                
                
    def processMessageQueue(self):
        while True:
            message = self._message_queue.get(True)
            
            if message is None:
                Logger.debug(self, "No message found in processMessageQueue, skipping...")
                continue
            
            #Logger.debug(self, "Message queue found message to send.")
            
            if time.time() - self._last_message_sent < self.MIN_DELAY_BETWEEN_MESSAGES:
                sleep_time = self.MIN_DELAY_BETWEEN_MESSAGES - (time.time() - self._last_message_sent)
                Logger.debug(self, "Recently sent a message. Sleeping for %f seconds..." % sleep_time)
                time.sleep(sleep_time)
            
            #Logger.debug(self, "Message queue sending message.")     
            self.sendMessage(message)
    
    

    