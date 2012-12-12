from babelpr.chatmedium import AbstractChatMedium
from babelpr.logger import Logger
from babelpr.Message import Message

import irclib
import time
import string

class IrcChatMedium(AbstractChatMedium):
    
    def __init__(self, chatbot, alias, config):
        AbstractChatMedium.__init__(self, chatbot, alias, config)
        self._irc = None
    
    def start(self):
        super(IrcChatMedium, self).start()
        
        while True:
            Logger.debug(self, "Starting IrcChat for '%s'" % self._alias)
            self._irc = IRCBot(self)
            self._irc.my_connect()
            Logger.warning(self, "IrcChat loop for '%s' ended" % self._alias)
            time.sleep(10)
            
    def sendMessage(self, message):
        AbstractChatMedium.sendMessage(self, message)
        self._irc.connection.privmsg(message.channel_id, message.body)
        
    def getChannels(self):
        return self._irc.channels
                
    def getOwnId(self):
        return self._config['bot_nick']
            
    def getRoster(self):
        return {}
    
    def onIrcMessage(self, message):
        self._chatbot.receiveMessage(message)

class IRCBot(irclib.SimpleIRCClient):
    def __init__(self, chat_medium):
        irclib.SimpleIRCClient.__init__(self)
        self._chat_medium = chat_medium
        self._last_connect_time = time.time() - 1000
        self.channels = []
        
    def my_connect(self):
        config = self._chat_medium._config
        
        Logger.info(self._chat_medium, "IRC Bot Connecting  u:%s n:%s" % (config['bot_nick'], config['server']))
        time_since_last_connect = time.time() - self._last_connect_time
        if time_since_last_connect < 10:
            time.sleep(10-time_since_last_connect)
            
        self._last_connect_time = time.time()
        connected = False
        while not connected:
            try:
                self.connect(config['server'], config['port'], config['bot_nick'])
            except Exception, e:
                Logger.info(self._chat_medium, "Could not connect to irc server: %s" % e)
                time.sleep(30)
            else:
                connected = True
                
        Logger.info(self._chat_medium, "IRC Bot starting processing loop.")
        self.start()
        Logger.info(self._chat_medium, "Exiting my connection function.")

    def on_welcome(self, connection, event):
        config = self._chat_medium._config
        
        Logger.info(self._chat_medium, "IRC Bot identifying with nickserv.")
        self.connection.privmsg("nickserv","identify %s" % config['password'])
        time.sleep(3)
        Logger.info(self._chat_medium, "Joining channels...")
        for channel in config['channels']:
            password = ""
            Logger.info(self._chat_medium, "Joining channel: %s" % channel)
            connection.join(channel + " " + password)
            self.channels.append(channel)
        Logger.info(self._chat_medium, "Finished joining channels.")
        

    def on_pubmsg(self, connection, event):
        body = string.join(event.arguments(), " ")
        sender = event.source()
        sendern = sender[0:sender.find("!")]
        channel = event.target()
        
        Logger.info(self._chat_medium, "Pubmsg: %s in %s said %s" % (sendern, channel, body))
        med = self._chat_medium
        message = Message(med._alias, med.getMediumName(), med.CHANNEL_TYPE_GROUP, channel, sendern, sendern, body)
        self._chat_medium.onIrcMessage(message)

        

    def on_privmsg(self, connection, event):
        body = string.join(event.arguments(), " ")
        sender = event.source()
        sendern = sender[0:sender.find("!")]
        
        Logger.info(self._chat_medium, "Privmsg: %s said %s" % (sendern, body))
        med = self._chat_medium
        message = Message(med._alias, med.getMediumName(), med.CHANNEL_TYPE_INDIVIDUAL, sendern, sendern, sendern, body)
        self._chat_medium.onIrcMessage(message)

        

    def on_disconnect(self, connection, event):
        Logger.info(self._chat_medium, "Warning: IRC Has disconnected.")
        self.my_connect()