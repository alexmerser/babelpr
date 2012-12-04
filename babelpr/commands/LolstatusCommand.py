from babelpr.commands import TriggeredCommand
from babelpr import Message
from babelpr.chatbot import ChatBot
from xml.dom import minidom


class LolstatusCommand(TriggeredCommand):
    triggers = ['lolstatus']
    name = 'lolstatus'
    description = "Gets status of a League of Legends summoner"
    syntax = "#lolstatus SUMMONER"

    def processCommand(self, message, arguments):
        assert isinstance(message, Message.Message)
        assert isinstance(self._chatbot, ChatBot)
        
        arguments = arguments.strip()
        if len(arguments) == 0:
            return "A summoner name is required.  Syntax: %s" % self.syntax
        
        summoner_name = arguments.lower()
        
        medium_alias = "lol"
        if not self._chatbot._mediums.has_key(medium_alias):
            return "I am not set up to connect to League of Legends"
        
        roster = self._chatbot._mediums[medium_alias]._xmpp.client_roster
        summoner_resource = None
        online = self._chatbot._mediums[medium_alias].getRoster()
        
        for jid,name in online.iteritems():
            presence = roster.presence(jid)
            main_resource = None
            for resource_id,resource, in presence.iteritems():
                main_resource = resource
                break
            
            if main_resource is None:
                continue
            
            if name.lower() == summoner_name:
                summoner_resource = main_resource
            
        if summoner_resource is None:
            return "Summoner '%s' is offline" % arguments
        
        if not summoner_resource.has_key('status'):
            return "Summoner '%s' is online, but status is unknown" % arguments
        
        try:
            xml = summoner_resource['status']
            doc = minidom.parseString(xml)
        except:
            return "Summoner '%s' is online, but I was unable to parse their status" % arguments
        
        gameStatus = getTagValue(doc, 'gameStatus')
        if gameStatus is None:
            gameStatusText = " has no game status"
        else:
            gameStatusText = " is %s" % gameStatus


        gameQueueType = getTagValue(doc, 'gameQueueType')
        if gameQueueType is None or gameQueueType == "NONE":
            gameQueueTypeText = ""
        else:
            gameQueueTypeText = " of type %s" % gameQueueType
        
        statusMsg = getTagValue(doc, 'statusMsg')
        if statusMsg is None:
            statusMsgText = ""
        else:
            statusMsgText = " with status of \"%s\"" % statusMsg
        
        
        
        status = "%s%s%s%s" % (arguments, gameStatusText, gameQueueTypeText, statusMsgText)
        
        return status
        

def getTagValue(doc, tag):
    matches = doc.getElementsByTagName(tag)
    if len(matches) == 0:
        return None
    
    try:
        value = matches[0].childNodes[0].nodeValue
    except:
        value = None
        
    return value
