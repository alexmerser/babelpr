from babelpr.chatmedium import AbstractChatMedium
from babelpr.logger import Logger
from babelpr.Message import Message

import irc.bot
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
            self._irc.start()
            Logger.warning(self, "IrcChat loop for '%s' ended" % self._alias)
            time.sleep(10)
            
    def sendMessage(self, message):
        AbstractChatMedium.sendMessage(self, message)
        self._irc.connection.privmsg(message.channel_id, message.body)
        
    def getChannels(self):
        channels = []
        for channel in self._irc.channels:
            channels.append(str(channel))
        return channels
                
    def getOwnId(self):
        return self._config['bot_nick']
    
    def formatTunnelMessage(self, sender_nick, medium_alias, body):
        #return AbstractChatMedium.formatTunnelMessage(self, sender_nick, medium_alias, body)
        return "%(nick_color)s%(nick)s %(parens_color)s(%(medium_color)s%(medium)s%(parens_color)s)%(colon_color)s: %(body_color)s%(body)s" % {
          'nick_color': self.getIrcColor(2),
          'nick': sender_nick,
          'parens_color': self.getIrcColor(1),
          'medium_color': self.getIrcColor(9),
          'medium': medium_alias,
          'colon_color': self.getIrcColor(1),
          'body_color': self.getIrcColor(1),
          'body': body
        }
        
    def getIrcColor(self, color_id):
        return chr(3) + str(color_id)# + ',0'
            
    def getRoster(self):
        roster = {}
        for chname, chobj in self._irc.channels.items():
            users = chobj.users()
            for user in users:
                if(str(user)) != self.getOwnNick():
                    roster[str(user)] = {
                    'name': str(user),
                    'special': False
                }
        return roster
    
    def onIrcMessage(self, message):
        self._chatbot.receiveMessage(message)

class IRCBot(irc.bot.SingleServerIRCBot):
    def __init__(self, chat_medium):
        config = chat_medium._config
        irc.bot.SingleServerIRCBot.__init__(self, [(config['server'], 6667)], config['bot_nick'], config['bot_nick'])
        self._chat_medium = chat_medium

    def start(self):
        Logger.info(self._chat_medium, "IRC Bot starting processing loop.")
        irc.bot.SingleServerIRCBot.start(self)        
        Logger.info(self._chat_medium, "Exiting my connection function.")
        
        
    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")        
        
        
    def on_welcome(self, c, e):
        config = self._chat_medium._config
        
        Logger.info(self._chat_medium, "IRC Bot identifying with nickserv.")
        self.connection.privmsg("nickserv","identify %s" % config['password'])
        time.sleep(3)
        Logger.info(self._chat_medium, "Joining channels...")
        
        for channel in config['channels']:
            Logger.info(self._chat_medium, "Joining channel: %s" % channel)
            c.join(channel)

    def on_pubmsg(self, connection, event):
        body = string.join(event.arguments, " ")
        sendern = event.source.nick
        channel = event.target
        
        Logger.info(self._chat_medium, "Pubmsg: %s in %s said %s" % (sendern, channel, body))
        med = self._chat_medium
        message = Message(med._alias, med.getMediumName(), med.CHANNEL_TYPE_GROUP, channel, sendern, sendern, body)
        self._chat_medium.onIrcMessage(message)

        

    def on_privmsg(self, connection, event):
        body = string.join(event.arguments, " ")
        sendern = event.source.nick
        
        Logger.info(self._chat_medium, "Privmsg: %s said %s" % (sendern, body))
        med = self._chat_medium
        message = Message(med._alias, med.getMediumName(), med.CHANNEL_TYPE_INDIVIDUAL, sendern, sendern, sendern, body)
        self._chat_medium.onIrcMessage(message)

        

    def on_disconnect(self, connection, event):
        Logger.info(self._chat_medium, "Warning: IRC Has disconnected.")
        self.my_connect()