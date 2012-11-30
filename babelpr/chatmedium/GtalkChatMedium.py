from babelpr.chatmedium import AbstractChatMedium
from babelpr.logger import Logger
import sleekxmpp.stanza.message
import time

from sleekxmpp import ClientXMPP
from babelpr import Message
import babelpr

class GtalkChatMedium(AbstractChatMedium):
    _xmpp = None
    group_channel = None
    
    def __init__(self, chatbot, config):
        super(GtalkChatMedium, self).__init__(chatbot, config)
    
    def start(self):
        super(GtalkChatMedium, self).start()
        
        while True:
            Logger.debug(self, "Starting GtalkBot")
            self._xmpp = GtalkBot(self._config['username'], self._config['password'], self)
            self._xmpp.register_plugin('xep_0030') # Service Discovery
            self._xmpp.register_plugin('xep_0045') # Multi-User Chat
            self._xmpp.register_plugin('xep_0249') # Direct MUC Invitations
            self._xmpp.register_plugin('xep_0199') # XMPP Ping                     
            
            self._xmpp.add_event_handler("message", self.onGtalkMessage)
            self._xmpp.add_event_handler("groupchat_message", self.onGtalkGroupMessage)
            
            self._xmpp.connect(('talk.google.com', 5222))
            self._xmpp.process(threaded=False)
            
            self._xmpp = None
        
            Logger.warning(self, "GtalkBot process ended")
            time.sleep(10)
            
    def sendMessage(self, message):
        super(GtalkChatMedium, self).sendMessage(message)
        assert isinstance(message, babelpr.Message.Message)
        
        if(self._xmpp is None):
            return
        
        Logger.info(self, "Sending %s message to '%s': %s" % (message.channel_type, message.channel_id, message.body))
        
        mtype = "chat" if message.channel_type == "individual" else "groupchat"
        self._xmpp.send_message(message.channel_id, message.body, None, mtype)

            
    def onGtalkMessage(self, msg):
        assert isinstance(msg, sleekxmpp.stanza.message.Message)
        
        if not (msg['type'] in ('chat', 'normal')):
            return
        
        if(msg['body'] == self._config['invite_trigger']):
            if self.group_channel is None:
                #self.group_channel = "babelrusechat"+str(random.randint(0,100000))
                response_message = Message.Message(self.getMediumName(), "individual", msg['from'], None, "Sorry, I'm not in a channel and I don't know how to make them")
                self.sendMessage(response_message)
                
                
            room = "%s" % self.group_channel
            jid = "%s" % msg['from']
            reason = "Join up!"
            mfrom = self._xmpp.boundjid
            self._xmpp.plugin['xep_0045'].invite(room, jid, reason, mfrom)
            
            
        
        message = Message.Message(self.getMediumName(), "individual", msg['from'], msg['from'], msg['body'])
        self._chatbot.receiveMessage(message)
        
    def onGtalkGroupMessage(self, msg):
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
            Logger.debug(self, "Group message from self ignored")
            return
        
        message = Message.Message(self.getMediumName(), "group", channel_id, msg_from, msg['body'])
        self._chatbot.receiveMessage(message)
        
    def setGroupChannel(self, channel):
        if channel != self.group_channel:
            Logger.info(self, "Changing main group channel to '%s'" % channel)
            self.group_channel = channel
        

class GtalkBot(ClientXMPP):
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
        
    def onChatInvite(self, event):
        self._chat_medium.setGroupChannel(event['from'])
        self.plugin['xep_0045'].joinMUC(event['from'],
                                    self._chat_medium._config['chat_name'],
                                    wait=True)
