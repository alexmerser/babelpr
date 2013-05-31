from logger import Logger
from babelpr import chatmedium, Message
from babelpr.chatmedium import AbstractChatMedium
from threading import Thread
import time
from babelpr.commands import ImplicitCommand, ExplicitCommand
import os
from babelpr.globals import BabelGlobals
import re
import sqlite3

class InvalidConfigError(Exception): pass
class NoMediumsConfigured(Exception): pass
class UnknownChatMedium(Exception): pass
class InvalidChatMedium(Exception): pass
class ChatMediumThreadDied(Exception): pass
class ChatMediumInstanceDied(Exception): pass
class CommandImportFailure(Exception): pass
class InvalidCommandClass(Exception): pass


class ChatBot(object):
    ROSTER_EVENT_ENTER = 1
    ROSTER_EVENT_EXIT = 2
    
    
    def __init__(self, config):
        self._config = {}
        self._mediums = {}
        self._medium_rosters = {}
        self._threads = {}
        self._explicit_commands = {}
        self._implicit_commands = []
        self._trigger_re = []
        
        Logger.info(self, "Initializing...")
        
        # self.loadUserDb()
        self.loadConfig(config)
        self.loadMediums()
        self.loadCommands()

    def loadUserDb(self):
        user_dbfile = BabelGlobals.location + '/babelpr/commands/databases/_user_locations.db'
        try:
            self._user_db = sqlite3.connect(user_dbfile)
        except:
            Logger.warning(self, "Unable to load user DB file")
            self._user_db = None
            return
        
        try:
            c = self._user_db.cursor()
        except:
            Logger.warning(self, "Unable to get user DB cursor in loadUserDb")
            return
        
        try:
            sql = 'create table if not exists locations (user_uniqid, location)'
            c.execute(sql)
        except:
            Logger.warning(self, "Unable create user DB table in loadUserDb")
        
        try:
            c.close()
        except:
            pass
        

        

    def loadConfig(self, config):
        # do some basic validation of the config
        assert isinstance(config, dict)
        try:
            if not(type(config['ChatMediums']) == dict):
                raise InvalidConfigError("ChatMediums must be a dictionary")
        except KeyError:
            raise InvalidConfigError("No ChatMediums key in config")

        # loop over the config, and load the mediums
        self._config = config        
        

    def loadMediums(self):
        mediums = {}
        for alias,config in self._config['ChatMediums'].iteritems():
            assert isinstance(alias, unicode)
            
            if not config.has_key('medium'):
                raise InvalidChatMedium(alias)
            
            medium_classname = config['medium'].title() + "ChatMedium"
            try:
                importmodule = __import__("babelpr.chatmedium."+medium_classname, medium_classname)
            except ImportError:
                raise UnknownChatMedium(config['medium'])
            
            try:
                chatmedium = getattr(importmodule, "chatmedium")
                mediumclass = getattr(getattr(chatmedium, medium_classname), medium_classname)
            except AttributeError:
                raise InvalidChatMedium(alias)
                
            inst = mediumclass(self, alias, config)
            mediums[alias] = inst

        if len(mediums.keys()) == 0:
            raise NoMediumsConfigured

        self._mediums = mediums
        
    def loadCommands(self):
        for pattern in self._config['command_trigger_formats']:
            self._trigger_re.append(re.compile(pattern))
        
        global __location__
        commands_path = BabelGlobals.location + '/babelpr/commands'
        command_dir_list = os.listdir(commands_path)
        for command_dir_item in command_dir_list:
            parts = command_dir_item.split('.')
            if len(parts) != 2 or parts[1] != 'py' or parts[0] == '__init__':
                continue
            self.loadCommand(parts[0])
        
    def loadCommand(self, command_classname):
        try:
            importmodule = __import__("babelpr.commands."+command_classname, command_classname)
        except ImportError:
            raise CommandImportFailure(command_classname)
        
        try:
            commands = getattr(importmodule, "commands")
            command_class = getattr(getattr(commands, command_classname), command_classname)
        except AttributeError:
            raise InvalidCommandClass(command_classname)
            
        command = command_class(self)
        if isinstance(command, ImplicitCommand):
            self._implicit_commands.append(command)
        else:
            for trigger in command.triggers:
                self._explicit_commands[trigger.lower()] = command
        
    
    def start(self):
        Logger.info(self, "Starting...")
        for k,v in self._mediums.iteritems():
            assert isinstance(v, AbstractChatMedium)
            medium_thread = Thread(target=v.start, args=())
            medium_thread.start()
            self._threads[k] = medium_thread
            
        Logger.info(self, "All mediums started")
        
        while True:
            time.sleep(1)
            self.checkMediums()
            self.checkRosters()

    def checkRosters(self):
        if self._mediums is None:
            return
        
        for medium_alias,medium in self._mediums.iteritems():
            assert isinstance(medium, AbstractChatMedium)
            roster = medium.getRoster()
            if roster is None or len(roster) == 0:
                continue
            
            old_roster = None
            
            if(medium_alias in self._medium_rosters):
                old_roster = self._medium_rosters[medium_alias]

            self._medium_rosters[medium_alias] = roster
            
            self.handleRosterChange(medium, old_roster, roster)
            
    def handleRosterChange(self, medium, old_roster, new_roster):
        if old_roster is None or new_roster is None:
            return
        
        left = []
        for member_id,data in old_roster.iteritems():
            if member_id not in new_roster and data['name'] not in left:
                left.append(data['name'])
                    
        for name in left:
            self.announceRosterChange(medium, name, self.ROSTER_EVENT_EXIT)


        joined = []
        for member_id,data in new_roster.iteritems():
            if member_id not in old_roster and data['name'] not in joined:
                joined.append(data['name'])
                    
        for name in joined:
            self.announceRosterChange(medium, name, self.ROSTER_EVENT_ENTER)
                
                
                
    def announceRosterChange(self, source_medium, nickname, event_type):
        verb = "joined" if event_type == self.ROSTER_EVENT_ENTER else "left"
        message_body = "%s %s %s" % (nickname, verb, source_medium._alias)
        
        for medium_alias,medium in self._mediums.iteritems():
            if  medium_alias == source_medium._alias:
                continue
            
            channels = medium.getChannels()
            
            for channel in channels:
                response_message = Message.Message(
                    medium._alias, 
                    medium.getMediumName(), 
                    AbstractChatMedium.CHANNEL_TYPE_GROUP, 
                    channel, 
                    source_medium.getOwnId(), 
                    source_medium.getOwnNick(), 
                    message_body
                )
                #print response_message
                self.enqueueMessage(response_message)
        
                
    def checkMediums(self):
        for medium,thread in self._threads.iteritems():
            if not thread.isAlive():
                raise ChatMediumThreadDied(medium)
            
        for medium,instance in self._mediums.iteritems():
            if not instance.isAlive():
                raise ChatMediumInstanceDied(medium)
        
        # Logger.debug(self, "All mediums healthy")
        
    def enqueueMessage(self, message):
        self._mediums[message.medium_alias].enqueueMessage(message)
        
    def getExtendedMediumChannelsForMediumChannel(self, source_medium, source_channel):
        tunnels = source_medium.getTunnelsForChannel(source_channel)
        
        source_pair = (source_medium, source_channel)
        pairs = [source_pair]
        for tunnel in tunnels:
            for medium in self._mediums.itervalues():
                medium_channels = medium.getChannelsForTunnel(tunnel)
                for channel in medium_channels:
                    pair = (medium, channel)
                    pairs.append(pair)
                    
        return list(set(pairs))
                
        
        
    def receiveMessage(self, message):
        if message is None: 
            return
        assert isinstance(message, Message.Message)
        
        source_medium = self._mediums[message.medium_alias]
        
        tunnels = source_medium.getTunnelsForChannel(message.channel_id)
        for tunnel in tunnels:
            for medium in self._mediums.itervalues():
                medium.relayTunnelMessage(tunnel, message)
        
        
        response = self.checkCommandResponse(message)
        if response is not None:
            extended = self.getExtendedMediumChannelsForMediumChannel(source_medium, message.channel_id)
            for pair in extended:
                medium = pair[0]
                channel = pair[1]
                response_message = Message.Message(
                    medium._alias, 
                    medium.getMediumName(), 
                    message.channel_type, 
                    channel, 
                    source_medium.getOwnId(), 
                    source_medium.getOwnNick(), 
                    response
                )
                self.enqueueMessage(response_message)
            
    def checkCommandResponse(self, message):
        for command in self._implicit_commands:
            assert isinstance(command, ImplicitCommand)
            response = command.processMessage(message)
            if response is not None:
                return response
        
        command_format = self.parseCommandFormat(message)
        if command_format is not None:
            command_match = False
            trigger = command_format['trigger'].lower()
            if self._explicit_commands.has_key(trigger):
                command = self._explicit_commands[trigger]
                assert isinstance(command, ExplicitCommand)
                command_match = True
                response = command.processCommand(message, trigger, command_format['arguments'])
                if response is not None:
                    return response
                
            if not command_match:
                #return "Unknown command: '%s'" % trigger
                pass
        
        return None
    
    def parseCommandFormat(self, message):
        for regex in self._trigger_re:
            r = regex.search(message.body)
            if r:
                return r.groupdict()
        return None
    
    def getUniqueIdForSender(self, message):
        assert isinstance(message, Message.Message)
        medium_user_id = self._mediums[message.medium_alias].getUniqueIdForSender(message)
        if medium_user_id is None:
            return None
        return message.medium_alias + ':' + medium_user_id 
    
    def getUserLocation(self, user_uniqid):
        self.loadUserDb()
        
        if self._user_db is None:
            return None
        
        try:
            cursor = self._user_db.cursor()
        except:
            Logger.warning(self, "Unable to create user DB cursor in getUserLocation")
            self._user_db.close()
            return None
        
        ret = None
        try:
            cursor.execute('SELECT location FROM locations where user_uniqid=?', [user_uniqid])
            data = cursor.fetchall()
            if len(data) > 0:
                ret = data[0][0]
        except:
            pass
        
        try:
            cursor.close()
        except:
            pass
        
        self._user_db.close()
        
        return ret
    
    def getUserUniqueId(self, provided_nick, medium_alias):
        medium_user_id = self._mediums[medium_alias].getUserUniqueId(provided_nick)
        if medium_user_id is None:
            return None
        return medium_alias + ':' + medium_user_id
    
    def getUserNick(self, user_uniqid, medium_alias):
        parts = user_uniqid.split(':', 1)
        return self._mediums[medium_alias].getUserNick(parts[len(parts)-1])
    
    def storeUserLocation(self, user_uniqid, location):
        self.loadUserDb()
        
        if self._user_db is None:
            return
        
        try:
            cursor = self._user_db.cursor()
        except:
            Logger.warning(self, "Unable to create user DB cursor in storeUserLocation")
            return
        
        try:
            cursor.execute('delete from locations where user_uniqid = ?', [user_uniqid])
            cursor.execute('insert into locations values (?,?)', [user_uniqid, location])
            self._user_db.commit()
        except:
            pass
        
        try:
            cursor.close()
        except:
            pass
        
        self._user_db.close()
        
