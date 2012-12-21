from babelpr.commands import ExplicitCommand
from babelpr import Message
from babelpr.chatbot import ChatBot
from babelpr.utils import isInt, getZipDistance


class DistanceCommand(ExplicitCommand):
    
    def __init__(self, chatbot):
        ExplicitCommand.__init__(self, chatbot)
        
        self.triggers = ['distance']
        self.name = 'distance'
        self.description = "Calculates the distance between two people"
        self.syntax = "#distance person[, person2]"
        

    def processCommand(self, message, trigger, arguments):
        assert isinstance(message, Message.Message)
        assert isinstance(self._chatbot, ChatBot)
        
        arguments = arguments.strip()
        if len(arguments) == 0:
            return "Syntax: " + self.syntax
        
        if arguments.find(',') != -1:
            parts = arguments.split(',',1)
            person1 = self._chatbot.getUserUniqueId(parts[0].strip(), message.medium_alias)
            if person1 is None:
                return "Sorry, I don't know who '%s' is" % parts[0].strip()
            person1nick = self._chatbot.getUserNick(person1, message.medium_alias)
            person1_missing_str = person1nick+" is"
            person1_nonint = person1nick+"'s"
            
            person2 = self._chatbot.getUserUniqueId(parts[1].strip(), message.medium_alias)
            if person2 is None:
                return "Sorry, I don't know who '%s' is" % parts[1].strip()
            person2nick = self._chatbot.getUserNick(person2, message.medium_alias)
            person2_missing_str = person2nick+" is"
            person2_nonint = person2nick+"'s"
            
        else:
            person1 = self._chatbot.getUniqueIdForSender(message)
            if person1 is None:
                return "Sorry, I don't know who you are"
            person1nick = "you"
            person1_missing_str = "you are"
            person1_nonint = "your"
            
            person2 = self._chatbot.getUserUniqueId(arguments, message.medium_alias)
            if person2 is None:
                return "Sorry, I don't know who '%s' is" % arguments
            person2nick = self._chatbot.getUserNick(person2, message.medium_alias)
            person2_missing_str = person2nick+" is"
            person2_nonint = person2nick+"'s"
            
            
            
        location1 = self._chatbot.getUserLocation(person1)
        if location1 is None:
            return "Sorry, I don't know where %s" % person1_missing_str
        if not isInt(location1):
            return "Sorry, I can only calculate distance between zips, and %s location is '%s'" % (person1_nonint, location1)
         
        location2 = self._chatbot.getUserLocation(person2)
        if location2 is None: 
            return "Sorry, I don't know where %s" % person2_missing_str
        if not isInt(location2):
            return "Sorry, I can only calculate distance between zips, and %s location is '%s'" % (person2_nonint, location2)
        
        distance = getZipDistance(location1, location2)
        if distance is None or distance < 0:
            return "Sorry, I don't know the distance between %s and %s" % (person1nick, person2nick)
        
        return "The distance between %s and %s is %s miles" % (person1nick, person2nick, distance)
    