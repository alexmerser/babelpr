from babelpr.chatmedium import AbstractChatMedium
from babelpr.logger import Logger
import sleekxmpp.stanza.message
import time

from sleekxmpp import ClientXMPP
from babelpr import Message
import babelpr

class JabberChatMedium(AbstractChatMedium, ClientXMPP):
    _xmpp = None
    _last_group_channel = None
    
    def start(self):
        super(JabberChatMedium, self).start()
        
        while True:
            Logger.debug(self, "Starting JabberChat for '%s'" % self._alias)
            self._xmpp = JabberBot(self._config['username'], self._config['password'], self)
            self._xmpp.register_plugin('xep_0030') # Service Discovery
            self._xmpp.register_plugin('xep_0045') # Multi-User Chat
            self._xmpp.register_plugin('xep_0249') # Direct MUC Invitations
            self._xmpp.register_plugin('xep_0199') # XMPP Ping                     
            
            self._xmpp.add_event_handler("message", self.onJabberMessage)
            self._xmpp.add_event_handler("groupchat_message", self.onJabberGroupMessage)
            
            use_ssl = self._config.has_key('use_ssl') and self._config['use_ssl']
            self._xmpp.connect((self._config['server'], self._config['port']), use_ssl=use_ssl)
            self._xmpp.process(threaded=False)
            
            self._xmpp = None
        
            Logger.warning(self, "JabberChat loop for '%s' ended" % self._alias)
            time.sleep(10)
            
    def sendMessage(self, message):
        super(JabberChatMedium, self).sendMessage(message)
        assert isinstance(message, babelpr.Message.Message)
        
        if(self._xmpp is None):
            return
        
        Logger.info(self, "%s sending %s message to '%s': %s" % (self._alias, message.channel_type, message.channel_id, message.body))
        
        mtype = "chat" if message.channel_type == "individual" else "groupchat"
        self._xmpp.send_message(message.channel_id, message.body, None, mtype)

            
    def onJabberMessage(self, msg):
        assert isinstance(msg, sleekxmpp.stanza.message.Message)
        
        if not (msg['type'] in ('chat', 'normal')):
            return
        
        if(msg['body'] in self._config['invite_triggers']):
            if self._last_group_channel is None:
                response_message = Message.Message(self.getMediumName(), "individual", msg['from'], None, "Sorry, I'm not in a channel and I don't know how to make them")
                self.sendMessage(response_message)
                
                
            room = "%s" % self._last_group_channel
            jid = "%s" % msg['from']
            reason = "Join up!"
            mfrom = self._xmpp.boundjid()
            self._xmpp.plugin['xep_0045'].invite(room, jid, reason, mfrom)
            
            
        
        message = Message.Message(self._alias, self.getMediumName(), "individual", msg['from'], msg['from'], msg['body'])
        self._chatbot.receiveMessage(message)
        
    def onJabberGroupMessage(self, msg):
        assert isinstance(msg, sleekxmpp.stanza.message.Message)
        
        if not (msg['type'] in ('groupchat')):
            return
        
        parts = ("%s" % msg['from']).split('/')
        if len(parts) > 1:
            channel_id = parts[0]
            msg_from = parts[1]
        else:
            channel_id = parts[0]
            msg_from = parts[0]
            
        self.setGroupChannel(channel_id)
        
        if(msg_from == self._config['chat_name']):
            #Logger.debug(self, "Group message from self ignored")
            return
        
        message = Message.Message(self._alias, self.getMediumName(), "group", channel_id, msg_from, msg['body'])
        self._chatbot.receiveMessage(message)
        
    def setGroupChannel(self, channel):
        if channel != self._last_group_channel:
            Logger.info(self, "%s changing main group channel to '%s'" % (self._alias, channel))
            self._last_group_channel = channel
            
    def getOwnId(self):
        return ('%s' % self._xmpp.boundjid).split('/')[0]
            
    def getRoster(self):
        roster = {}
        my_id = self.getOwnId()
        
        for jid in self._xmpp.client_roster:
            if jid == my_id:
                continue
            
            user = self._xmpp.client_roster[jid]
            presence = self._xmpp.client_roster.presence(jid)
            main_resource = None
            for name,resource, in presence.iteritems():
                main_resource = resource
                break
            
            if main_resource is None:
                continue
            
            name = user['name'] if len(user['name']) > 0 else jid 
            roster[jid] = name
        
        
        return roster
        

class JabberBot(ClientXMPP):
    _chat_medium = None

    def __init__(self, jid, password, chat_medium):
        ClientXMPP.__init__(self, jid, password)
        self._chat_medium = chat_medium
        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("groupchat_invite", self.onChatInvite)
        self.add_event_handler("groupchat_direct_invite", self.onChatInvite)

    def session_start(self, event):
        self.send_presence()
        self.get_roster()
        
        for channel in self._chat_medium._config['channels']:
            Logger.info(self._chat_medium, "Attempting to join '%s'" % channel)
            self.plugin['xep_0045'].joinMUC(channel,
                                    self._chat_medium._config['chat_name'],
                                    wait=True)
        
    def onChatInvite(self, event):
        self._chat_medium.setGroupChannel(event['from'])
        self.plugin['xep_0045'].joinMUC(event['from'],
                                    self._chat_medium._config['chat_name'],
                                    wait=True)
