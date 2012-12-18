from babelpr.chatmedium import AbstractChatMedium
from babelpr.logger import Logger
import sleekxmpp.stanza.message
import time

from sleekxmpp import ClientXMPP
import babelpr
import re
from babelpr.Message import Message

class JabberChatMedium(AbstractChatMedium, ClientXMPP):
    cdata_pattern = '^<!\[CDATA\[(.*)\]\]>$'
    cdata_re = re.compile(cdata_pattern,re.MULTILINE|re.DOTALL)
    
    def __init__(self, chatbot, alias, config):
        self._xmpp = None
        AbstractChatMedium.__init__(self, chatbot, alias, config)
    
    def start(self):
        super(JabberChatMedium, self).start()
        
        while True:
            Logger.debug(self, "Starting JabberChat for '%s'" % self._alias)
            self._xmpp = JabberBot(self._config['username'], self._config['password'], self)
            self._xmpp.register_plugin('xep_0030') # Service Discovery
            self._xmpp.register_plugin('xep_0045') # Multi-User Chat
            #self._xmpp.register_plugin('xep_0249') # Direct MUC Invitations
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
        
        mtype = "chat" if message.channel_type == self.CHANNEL_TYPE_INDIVIDUAL else "groupchat"
        self._xmpp.send_message(message.channel_id, message.body, None, mtype)

    def digestJabberMessage(self, msg):
        assert isinstance(msg, sleekxmpp.stanza.message.Message)
        
        if not (msg['type'] in ('chat', 'normal', 'groupchat')):
            return None
        
        body = msg['body']
        matches = self.cdata_re.findall(body)
        if len(matches) > 0:
            body = matches[0]
            
        parts = ("%s" % msg['from']).split('/')
        if len(parts) > 1:
            channel_id = parts[0]
            msg_from = parts[1]
        else:
            channel_id = parts[0]
            msg_from = parts[0]
            
        msg_from_str = "%s" % msg_from
            
        if msg_from_str == self.getOwnNick() or msg_from_str == "%s" % self._xmpp.boundjid:
            return None
            
        from_nick = self._xmpp.getNick(msg_from)
        if from_nick is None:
            from_nick = self._xmpp.getNick(msg['from'])
            
        if from_nick is None:
            from_nick = msg_from
        
        channel_type = self.CHANNEL_TYPE_GROUP if msg['type'] == 'groupchat' else self.CHANNEL_TYPE_INDIVIDUAL
        
        message = Message(self._alias, self.getMediumName(), channel_type, channel_id, msg_from, from_nick, body)
        return message
        
            
    def onJabberMessage(self, msg):
        message = self.digestJabberMessage(msg)
        self._chatbot.receiveMessage(message)
        
    def onJabberGroupMessage(self, msg):
        pass
        
    def getChannels(self):
        rooms = self._xmpp.plugin['xep_0045'].rooms
        channels = []
        for room_jid in rooms:
            channels.append(("%s" % room_jid).split('/')[0])
        return channels
                
    def getOwnId(self):
        return ('%s' % self._xmpp.boundjid).split('/')[0]
            
    def getRoster(self):
        roster = {}
        my_id = self.getOwnId()
        rooms = self._xmpp.plugin['xep_0045'].rooms
        
        
        for room_jid in rooms:
            members = rooms[room_jid]
            for member_id,member_data in members.iteritems():
                channel_member_jid = "%s/%s" % (room_jid, member_id)
                
                #try to get the jid from the room's member record
                if member_data.has_key('jid') and member_data['jid'] is not None and member_data['jid'] != '':
                    jid = member_data['jid']
                    
                    # try to get a nick from that jid
                    nick = self._xmpp.getNick(jid)
                    
                    if nick is None:
                        # if we didn't get a nick, then try to get it from the channel ID 
                        nick = self._xmpp.getNick(channel_member_jid)
                    
                    if nick is None:
                        # if we still didn't get a nick, then fall back to the channel member_id
                        nick = member_id
                else:
                    # no true JID found.  use the channel member JID instead
                    # and try to parse a nick from it
                    jid = channel_member_jid
                    nick = self._xmpp.getNick(channel_member_jid)
                        

                # if we didn't get a nick, then just use the ID they provide to the channel
                if nick is None or nick == channel_member_jid:
                    nick = member_id
                
                if jid == self._xmpp.boundjid:
                    continue
                
                roster[channel_member_jid] = {
                    'name': nick,
                    'special': False
                }
        
                
        for node_domain in self._xmpp.client_roster:
            if node_domain == my_id:
                continue
            
            if node_domain in rooms:
                continue
            
            presence = self._xmpp.client_roster.presence(node_domain)
            main_resource = None
            main_nick = None
            main_jid = None
            
            for resource_id,resource, in presence.iteritems():
                if main_resource is None:
                    main_resource = resource
                    main_jid = node_domain + '/' + resource_id
                
                if main_nick is None:
                    jid = node_domain + '/' + resource_id
                    nick = self._xmpp.getNick(jid)
                    if nick is not None:
                        main_jid = jid
                        main_nick = nick
            
            if main_resource is None:
                continue            
            
            if nick is None:
                nick = node_domain
            
            roster[main_jid] = {
              'name': nick,
              'special': False
            }

        
        return roster

class JabberBot(ClientXMPP):
    nick_pattern = 'from="(?P<from>.*?)".*jid="(?P<jid>.*?)" role.*\<nick xmlns="http:\/\/jabber\.org\/protocol\/nick"\>(?P<nick>.*?)\<\/nick\>'
    nick_re = re.compile(nick_pattern,re.MULTILINE|re.DOTALL)
    
    def __init__(self, jid, password, chat_medium):
        ClientXMPP.__init__(self, jid, password)
        self.chatnick_to_nick = {}
        self.jid_to_nick = {}
        
        self._chat_medium = chat_medium
        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("groupchat_invite", self.onChatInvite)
        self.add_event_handler("groupchat_direct_invite", self.onChatInvite)
        self.add_event_handler("changed_status", self.onChangedStatus)
        self.add_event_handler("got_online", self.onChangedStatus)

    def session_start(self, event):
        Logger.info(self._chat_medium, "Jabber Session Starting...")
        self.plugin['xep_0045'].rooms = {}
        
        self.send_presence()
        self.get_roster()
        
        
        if self._chat_medium._config.has_key('channels'):
            for channel in self._chat_medium._config['channels']:
                Logger.info(self._chat_medium, "Attempting to join '%s'" % channel)
                self.plugin['xep_0045'].joinMUC(channel, self._chat_medium.getOwnNick(), wait=True, pfrom=self.boundjid)
        
    def onChangedStatus(self, event):
        try:
            # let them know we can do MUC
            jid = event.get_from()
            if jid not in self.plugin['xep_0045'].rooms and jid != self.boundjid:        
                data = '<presence to="%s" from="%s"><status /><priority>24</priority><c xmlns="http://jabber.org/protocol/caps" node="http://mail.google.com/xmpp/client/caps" ext="pmuc-v1" ver="1.1" /></presence>'
                self.send_raw(data % (jid, self.boundjid))
        except:
            pass
            
            
        
        event_str = "%s" % event
        
        if event_str.find('<nick') > 0:
            matches = self.nick_re.search(event_str)
            if matches is None:
                return
            
            group = matches.groupdict()
            from_parts = group['from'].split('/')
            
            rooms = self.plugin['xep_0045'].rooms
            if rooms.has_key(from_parts[0]):
                self.chatnick_to_nick[from_parts[1]] = group['nick']
                
                user_parts = group['jid'].split('/')
                if len(user_parts) == 2:
                    self.jid_to_nick[group['jid']] = group['nick']
                
            
            
            
                
    def getNick(self, person):
        if person is None:
            return None
        person = "%s" % person
        
        rooms = self.plugin['xep_0045'].rooms
        person_parts =  person.split('/')
        
        if len(person_parts) == 2 and rooms.has_key(person_parts[0]):
            if self.chatnick_to_nick.has_key(person_parts[1]):
                return self.chatnick_to_nick[person_parts[1]]
        
        if person_parts[0] in self.client_roster:
            user = self.client_roster[person_parts[0]]
            if len(user['name']) > 0:
                return user['name']
            
        if self.jid_to_nick.has_key(person):
            return self.jid_to_nick[person]
        
        return None

        
    def onChatInvite(self, event):
        self._chat_medium.setGroupChannel(event['from'])
        self.plugin['xep_0045'].joinMUC(event['from'],
                                    self._chat_medium.getOwnNick(),
                                    wait=True)
