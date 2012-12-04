from babelpr.logger import Logger

class AbstractChatMedium(object):
    _config = {}
    _chatbot = {}
    _isAlive = True
    _alias = None
    
    def __init__(self, chatbot, alias, config):
        Logger.info(self, "%s %s initalizing..." % (alias, config['medium']))
        self._alias = alias
        self._config = config
        self._chatbot = chatbot
    
    def start(self):
        Logger.info(self, "%s %s starting..." % (self._alias, self._config['medium']))

    def isAlive(self):
        return self._isAlive
    
    def sendMessage(self, message):
        pass
    
    def getMediumName(self):
        return self._config['medium']
    
    def getRoster(self):
        return {}
    
    def getOwnId(self):
        return None
