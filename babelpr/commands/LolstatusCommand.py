from babelpr.commands import TriggeredCommand
from babelpr import Message
from babelpr.chatbot import ChatBot
from xml.dom import minidom
import time
import datetime


class LolstatusCommand(TriggeredCommand):
    triggers = ['lolstatus']
    name = 'lolstatus'
    description = "Gets status of a League of Legends summoner"
    syntax = "#lolstatus SUMMONER"

    def processCommand(self, message, trigger, arguments):
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
        
        for jid,data in online.iteritems():
            presence = roster.presence(jid)
            main_resource = None
            for resource_id,resource, in presence.iteritems():
                main_resource = resource
                break
            
            if main_resource is None:
                continue
            
            if data['name'].lower() == summoner_name:
                summoner_resource = main_resource
                summoner_name = data['name']
            
        if summoner_resource is None:
            return "Summoner '%s' is offline" % arguments
        
        if not summoner_resource.has_key('status'):
            return "Summoner '%s' is online, but status is unknown" % summoner_name
        
        try:
            xml = summoner_resource['status']
            doc = minidom.parseString(xml)
        except:
            return "Summoner '%s' is online, but I was unable to parse their status" % summoner_name
        
        status = summoner_name
        
        gameStatus = getTagValue(doc, 'gameStatus')
        if gameStatus is None:
            status += " has no game status"
        else:
            inGame = False
            if gameStatus == "inGame":
                gameStatus = "in game"
                inGame = True
            if gameStatus == "inQueue":
                gameStatus = "in queue"
            if gameStatus == "championSelect":
                gameStatus = "in champion select"
            elif gameStatus == "outOfGame":
                gameStatus = "out of game"
            
            status += " is %s" % gameStatus
            
            if inGame:
                gameQueueType = getTagValue(doc, 'gameQueueType')
                if gameQueueType is not None and gameQueueType != "NONE":
                    status += " of type %s" % gameQueueType
                
                skinname = getTagValue(doc, 'skinname')
                if skinname is not None and len(skinname) > 0:
                    status += " playing as %s" % skinname

                timeStamp = getTagValue(doc, 'timeStamp')
                if timeStamp is not None:
                    try:
                        duration = time.time() - int(timeStamp) / 1000
                        sec = datetime.timedelta(seconds=duration)
                        d = datetime.datetime(1,1,1) + sec
                        parts = []
                        if d.day - 1 == 1:
                            parts.append("%s day" % (d.day - 1))
                        elif d.day - 1 > 1:
                            parts.append("%s days" % (d.day - 1))
                            
                        if d.hour == 1:
                            parts.append("%s hour" % (d.hour))
                        elif d.hour > 1:
                            parts.append("%s hours" % (d.hour))
                        
                        if d.minute == 1:  
                            parts.append("%s min" % (d.minute))
                        elif d.minute > 1:
                            parts.append("%s mins" % (d.minute))
                            
                        if len(parts) > 0:
                            status += " for %s" % ", ".join(parts)
                        
                    except:
                        pass
                
        
        statusMsg = getTagValue(doc, 'statusMsg')
        if statusMsg is not None:
            status += " with status of \"%s\"" % statusMsg
        
        
        
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
