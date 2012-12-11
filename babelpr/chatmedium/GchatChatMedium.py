from babelpr.chatmedium.JabberChatMedium import JabberChatMedium
from babelpr.logger import Logger

class GchatChatMedium(JabberChatMedium):
    
    def __init__(self, chatbot, alias, config):
        JabberChatMedium.__init__(self, chatbot, alias, config)
        
        self._last_group_channel = None
        self.MIN_DELAY_BETWEEN_MESSAGES = 0.1

    def onJabberMessage(self, msg):
        message = self.digestJabberMessage(msg)
        self._chatbot.receiveMessage(message)
                
        if message is None:
            return
        
        if(self._config.has_key('invite_triggers') and message.body in self._config['invite_triggers']):
            if self._last_group_channel is None:
                self.sendBodyToTarget(self.CHANNEL_TYPE_INDIVIDUAL, msg['from'], "Sorry, I'm not in a channel and I don't know how to make one")
                
                
            room = "%s" % self._last_group_channel
            jid = "%s" % msg['from']
            reason = "Join up!"
            mfrom = self._xmpp.boundjid
            self._xmpp.plugin['xep_0045'].invite(room, jid, reason, mfrom)
        
    def onJabberGroupMessage(self, msg):
        message = self.digestJabberMessage(msg)
        if message is None:
            return
        
        self.setGroupChannel(message.channel_id)
        
        
    def setGroupChannel(self, channel):
        if channel != self._last_group_channel:
            Logger.info(self, "%s changing main group channel to '%s'" % (self._alias, channel))
            self._last_group_channel = channel
