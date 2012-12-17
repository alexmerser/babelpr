from logger import Logger
from babelpr import chatmedium, Message
from babelpr.chatmedium import AbstractChatMedium
from threading import Thread
import time
from babelpr.commands import ImplicitCommand, ExplicitCommand
import os
from babelpr.globals import BabelGlobals
import re

class InvalidConfigError(Exception): pass
class NoMediumsConfigured(Exception): pass
class UnknownChatMedium(Exception): pass
class InvalidChatMedium(Exception): pass
class ChatMediumThreadDied(Exception): pass
class ChatMediumInstanceDied(Exception): pass
class CommandImportFailure(Exception): pass
class InvalidCommandClass(Exception): pass


class ChatBot(object):
    
    def __init__(self, config):
        self._config = {}
        self._mediums = {}
        self._threads = {}
        self._explicit_commands = {}
        self._implicit_commands = []
        self._trigger_re = []
        
        Logger.info(self, "Initializing...")

        self.loadConfig(config)
        self.loadMediums()
        self.loadCommands()

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
            time.sleep(5)
            self.checkMediums()

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
        
