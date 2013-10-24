from babelpr import Message
from babelpr.chatbot import ChatBot
from babelpr.commands import ExplicitCommand
import time
import wolframalpha
import xml.etree.ElementTree


class CalcCommand(ExplicitCommand):
    
    def __init__(self, chatbot):
        ExplicitCommand.__init__(self, chatbot)
        
        self.triggers = ['calc']
        self.name = 'calc'
        self.description = "Attempts to calculate an expression, using Wolfram Alpha"
        self.syntax = "#calc EXPRESSION"
        
        self.wolfram_client = None
        if 'wolfram_api_key' in self._chatbot._config:
            key = self._chatbot._config['wolfram_api_key']
            if isinstance(key, basestring) and len(key) > 0: 
                self.wolfram_client = wolframalpha.Client(key)        

    def processCommand(self, message, trigger, arguments):
        assert isinstance(message, Message.Message)
        assert isinstance(self._chatbot, ChatBot)
        
        if self.wolfram_client is None:
            return "Unable to calculate: Wolfram Alpha API not configured"
        
        arguments = arguments.strip()
        if len(arguments) == 0:
            return "You must specify something to calculate."
        
        return self.getResult(arguments)
        
        
    def getResult(self, query):
        retried = 0
        result = None
        while retried < 5 and (result is None or result.isError()):
            if retried > 0:
                time.sleep(0.1)
            result = self.queryWolfram(query)
            retried = retried + 1
            
        if result is None:
            return "Unable to calculate: error when querying Wolfram Alpha client"
        
        if result.wolfram_error is not None:
            return "Error from Wolfram Alpha: %s" % result.wolfram_error
        
        if result.babel_error is not None:
            return result.babel_error
        
        return "%s: %s" % (query, result.response)
        
        
    def queryWolfram(self, query):
        res = None
        try:
            res = self.wolfram_client.query(query)
        except:
            res = None
        
        if res is None:
            return BabelWolframResult(wolfram_error="unable to query API")
        
        if isinstance(res.tree, xml.etree.ElementTree.ElementTree):
            assert isinstance(res.tree, xml.etree.ElementTree.ElementTree)
            error = res.tree.find('error')
            if error is not None:
                msg = error.find("msg")
                if msg is not None:
                    return BabelWolframResult(wolfram_error=msg.text)
        
        result = None
        try:
            element = next(res.results)
            result = element.text
        except:
            result = None
            
        if result is None:
            next_best = None
            try:
                for pod in res.pods:
                    try:
                        if pod.title == "Result":
                            result = pod.text
                            break
                        if pod.title != "Input" and next_best is None:
                            next_best = "%s (%s)" % (pod.text, pod.title) 
                    except:
                        continue
            except:
                result = None
            
            if next_best is not None and result is None:
                result = next_best 
            
        if result is None:
            return BabelWolframResult(babel_error="I don't know how to answer '%s'" % query)
        
        return BabelWolframResult(response = result)
    
    
class BabelWolframResult(object):
    def __init__(self, wolfram_error=None, babel_error=None, response=None):
        self.wolfram_error = wolfram_error
        self.babel_error = babel_error
        self.response = response
        
    def isError(self):
        return self.wolfram_error is not None or self.babel_error is not None