from logger import Logger
from babelpr import chatmedium, Message
from babelpr.chatmedium import AbstractChatMedium
from threading import Thread
import time
from babelpr.commands import GreedyCommand, TriggeredCommand
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
    _config = {}
    _mediums = {}
    _threads = {}
    _triggered_commands = {}
    _greedy_commands = []
    _trigger_re = []
    
    def __init__(self, config):
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
        if isinstance(command, GreedyCommand):
            self._greedy_commands.append(command)
        else:
            for trigger in command.triggers:
                self._triggered_commands[trigger] = command
        
    
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
        
    def sendMessage(self, message):
        self._mediums[message.medium_alias].sendMessage(message)
        
    def receiveMessage(self, message):
        assert isinstance(message, Message.Message)
        Logger.info(self, "Got message: %s / %s / %s / %s" % (message.channel_type, message.channel_id, message.sender, message.body))
        
        response = self.checkCommandResponse(message)
        if response is not None:
            response_message = Message.Message(message.medium_alias, message.medium_type, message.channel_type, message.channel_id, None, response)
            self.sendMessage(response_message)
            
    def checkCommandResponse(self, message):
        for command in self._greedy_commands:
            assert isinstance(command, GreedyCommand)
            response = command.processMessage(message)
            if response is not None:
                return response
        
        command_format = self.parseCommandFormat(message)
        if command_format is not None:
            command_match = False
            if self._triggered_commands.has_key(command_format['trigger']):
                command = self._triggered_commands[command_format['trigger']]
                assert isinstance(command, TriggeredCommand)
                command_match = True
                response = command.processCommand(message, command_format['arguments'])
                if response is not None:
                    return response
                
            if not command_match:
                #return "Unknown command: '%s'" % command_format['trigger']
                pass
        
        return None
    
    def parseCommandFormat(self, message):
        for regex in self._trigger_re:
            r = regex.search(message.body)
            if r:
                return r.groupdict()
        return None
        
