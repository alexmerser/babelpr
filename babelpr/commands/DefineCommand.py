from babelpr.commands import ExplicitCommand
from babelpr import Message
from babelpr.chatbot import ChatBot
from babelpr.utils import stripHTML, getWebpage
import xml.etree.ElementTree as et
import urllib
import re
import traceback

class DefineCommand(ExplicitCommand):
    
    def __init__(self, chatbot):
        ExplicitCommand.__init__(self, chatbot)
    
        self.triggers = ['define']
        self.name = 'define'
        self.description = "Checks various online dictionaries to define your word."
        self.syntax = "#define [mw#|google#|urban#] WORD"
    
    def processCommand(self, message, trigger, arguments):
        assert isinstance(message, Message.Message)
        assert isinstance(self._chatbot, ChatBot)
        
        args = arguments.strip()
        if args == "":
            return "Usage: #define word.  You may also specify either Merriam-Webster, Google, or UrbanDictionary as the source like this: #define mw#word, #define google#word, #define urban#word."
        else:
            key = self._chatbot._config['mw_api_key']

            if args.find("#") >= 0:
                dictionary = args.split("#")[0].upper()
                args = args[len(dictionary)+1:]
                
                if dictionary=="MW" or dictionary=="M-W" or dictionary=="Merriam-Webster":
                    result = DefineCommand.MWDefine(args, key)
                    if result[0]:
                        return "Merriam-Webster says '%s' means: %s" % (args, result[1])
                    else:
                        return "Merriam-Webster doesn't know what '%s' means." % args
                elif dictionary=="GOOGLE" or dictionary=="GOOGLEDEFINE":
                    result = DefineCommand.GoogleDefine(args)
                    if result[0]:
                        return "Google says '%s' means: %s" % (args, result[1])
                    else:
                        return "Google doesn't know what '%s' means." % args
                elif dictionary=="URBAN" or dictionary=="UD" or dictionary=="URBANDICTIONARY":
                    result = DefineCommand.UrbanDefine(args)
                    if result[0]:
                        if result[1].lower() == args:
                            return "UrbanDictionary says '%s' means: %s" % (args, result[2])
                        else:
                            return "UrbanDictionary's best match for '%s' is '%s': %s" % (args, result[1], result[2])
                    else:
                        return "UrbanDictionary doesn't know what '%s' means." % args
                else:
                    return "Unknown dictionary specified.  Please choose either Merriam-Webster, Google, or UrbanDictionary."
            else:
                result = DefineCommand.MWDefine(args, key)
                if result[0]:
                    return "Merriam-Webster says '%s' means: %s" % (args, result[1])
                else:
                    result = DefineCommand.GoogleDefine(args)
                    if result[0]:
                        return "Google says '%s' means: %s" % (args, result[1])
                    else:
                        result = DefineCommand.UrbanDefine(args)
                        if result[0]:
                            if result[1].lower() == args:
                                return "UrbanDictionary says '%s' means: %s" % (args, result[2])
                            else:
                                return "UrbanDictionary's best match for '%s' is '%s': %s" % (args, result[1], result[2])
                        else:
                            return "I don't know what '%s' means." % args
    
    @classmethod               
    def MWDefine(cls, word, key):
        try:
            url = "http://www.dictionaryapi.com/api/v1/references/collegiate/xml/%s?key=%s" % (urllib.quote(word), key)
            c = getWebpage(url)
            print c
            root = et.fromstring(c)
            answer = "".join(root.findall('.//dt')[0].itertext())
            if answer.find(":") == 0:
                answer = answer[1:]
            answer = answer.strip()
            if len(answer) > 150:
                answer = answer[:150]+"..."

            return [True, answer]

        except:
            print traceback.format_exc()
            return [False,""]


    @classmethod               
    def GoogleDefine(cls, word):
        closing_string = "</li>"
        starting_string = """<li style="list-style-type:decimal">"""
        try:
            c = getWebpage("http://www.google.com/search?hl=en&lr=&safe=off&c2coff=1&q=%s&btnG=Search" % urllib.quote("define:\"" + word + "\""))
        except:
            c = ""
        c = c.replace("\r","").replace("\n","")
        
        if c.find(starting_string) < 0:
            return [False,""]
        
        c = c.split(starting_string,1)[1]
        if c.find(closing_string) < 0:
            return [False,""]
        
        result = c.split(closing_string)[0].strip()
        if(result.find("<br>")):
            result = result.split("<br>")[0]
        if len(result) > 150:
            result = result[:150]+"..."
        result = stripHTML(result)
        return [True,result]

    @classmethod               
    def UrbanDefine(cls, word):
        try:
            c = getWebpage("http://www.urbandictionary.com/define.php?term=%s" % urllib.quote(word))
        except:
            c = ""
    
        ud_def_regex = """<div class='word'>.*?<a .*?>(.+?)</a>.*?<div class='meaning'>(.+?)</div>"""
        c = re.findall(ud_def_regex, c, re.MULTILINE| re.DOTALL)
        if len(c) > 0:
            word_result = stripHTML(c[0][0])
            def_result = stripHTML(c[0][1])
            def_result = def_result.replace('\n',' ')
            def_result = def_result.replace('  ',' ')
            def_result = def_result.replace('  ',' ')
            def_result = def_result.replace('  ',' ')
            if len(def_result) > 300:
                def_result = def_result[:300]+"..."
            return [True,word_result,def_result]
        else:
            return [False,None,None]

