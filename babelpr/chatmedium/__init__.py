from babelpr.logger import Logger

class AbstractChatMedium(object):
    _config = {}
    _chatbot = {}
    _isAlive = True
    
    def __init__(self, chatbot, config):
        Logger.info(self, "Initalizing...")
        self._config = config
        self._chatbot = chatbot
    
    def start(self):
        Logger.info(self, "Starting...")

    def isAlive(self):
        return self._isAlive
    
    def sendMessage(self, message):
        pass
    
    def getMediumName(self):
        classname = self.__class__.__name__
        mediumname = classname[:-10].lower()
        return mediumname
    
    
    
