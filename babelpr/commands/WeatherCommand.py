from babelpr.commands import ExplicitCommand
from babelpr import Message
from babelpr.chatbot import ChatBot
from babelpr.utils import stripHTML, getWebpage
import re
import urllib
from xml.dom import minidom

class WeatherCommand(ExplicitCommand):
    
    def __init__(self, chatbot):
        ExplicitCommand.__init__(self, chatbot)
        
        self.name = "weather"
        self.triggers = ["weather"]
        self.description = "Gets the weather at a location"
        self.syntax = "#weather LOCATION"
        self.woe_re = re.compile("<woeid>(?P<woeid>[^<]+)</woeid>")

    def processCommand(self, message, trigger, arguments):
        assert isinstance(message, Message.Message)
        assert isinstance(self._chatbot, ChatBot)

        lookup_type = None
        requestor = self._chatbot.getUniqueIdForSender(message)
        
        args = arguments.strip()
        if args == "":
            requestor_location = self._chatbot.getUserLocation(requestor)
            if requestor_location is None:            
                return "Sorry, I don't know where you are.  Use " + self.syntax
            lookup_location = requestor_location
            lookup_type = "REQUESTOR_LOCATION"
            
            woeid = None 
        else:
            lookup_location = args
            lookup_type = "SPECIFIED_LOCATION"
    
            user_uniqid = self._chatbot.getUserUniqueId(lookup_location, message.medium_alias)
            user_location = self._chatbot.getUserLocation(user_uniqid)
            woeid = self.getWOEID(user_location)
        
        if woeid is None:
            woeid = self.getWOEID(lookup_location)
            if woeid is None:
                if lookup_location != args:
                    return "Sorry, I thought you were in '%s' but I can't seem to find that location any more.  Please use %s" % (lookup_location, self.syntax)
                else:
                    return "Sorry, I don't know where/who that is"
                
        else:
            lookup_location = user_location
            lookup_type = "OTHER_USER_NAME"
            
        weather = self.getWeather(woeid)
        
        if weather is None:
            return "Sorry, I know who/where '%s' is, but I don't know the weather there." % lookup_location
        
        if lookup_type == "SPECIFIED_LOCATION":
            self._chatbot.storeUserLocation(requestor, lookup_location)
            
        if lookup_type == "OTHER_USER_NAME":
            prefix = "Weather for %s in %s: " % (self._chatbot.getUserNick(user_uniqid, message.medium_alias), weather[0])
        else:
            prefix = "Weather in %s: " % weather[0]
            
        
        return prefix + weather[1]

    def getWOEID(self, location):
        if location is None:
            return None
        
        url = "http://where.yahooapis.com/v1/places.q('%s')?appid=%s" % (urllib.quote(location), self._chatbot._config['yahoo_appid'])
        page = getWebpage(url)
        r = self.woe_re.search(page)
        
        if not r:
            return None
        
        d = r.groupdict()
        return d['woeid']
    
    def getWeather(self, woeid):
        if woeid is None:
            return None
        
        WEATHER_NS = 'http://xml.weather.yahoo.com/ns/rss/1.0'
        url = "http://weather.yahooapis.com/forecastrss?w=%s" % woeid
        
        condition = None
        location = None
        forecasts = []
        try:
            page = getWebpage(url)
            dom = minidom.parseString(page)
            for node in dom.getElementsByTagNameNS(WEATHER_NS, 'forecast'):
                forecasts.append({
                        'date': node.getAttribute('date'),
                        'low': node.getAttribute('low'),
                        'high': node.getAttribute('high'),
                        'condition': node.getAttribute('text')
                    })
            
            ylocation = dom.getElementsByTagNameNS(WEATHER_NS, 'location')[0]
            location = {
                'city': ylocation.getAttribute('city'),
                'region': ylocation.getAttribute('region')
            }
            
            ycondition = dom.getElementsByTagNameNS(WEATHER_NS, 'condition')[0]
            condition = {
                'current_condition': ycondition.getAttribute('text'),
                'current_temp': ycondition.getAttribute('temp')
            }
        except:
            condition = None
        
        if condition is None:
            return None
        
        str_location = "WOEID %s" % woeid if location is None else "%s, %s" % (location['city'], location['region'])
        
        return (str_location, "%s and %s degrees" % (condition['current_condition'], condition['current_temp']))
        
        
        