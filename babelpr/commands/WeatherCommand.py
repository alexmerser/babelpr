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

        args = arguments.strip()
        if args == "":
            return "Syntax: " + self.syntax
        
        woeid = self.getWOEID(args)
        if woeid is None:
            return "Sorry, I don't know where '%s' is" % args
        
        weather = self.getWeather(woeid)
        
        if weather is None:
            return "Sorry, I don't know the weather there."
        
        return weather

    def getWOEID(self, location):
        url = "http://where.yahooapis.com/v1/places.q('%s')?appid=%s" % (urllib.quote(location), self._chatbot._config['yahoo_appid'])
        page = getWebpage(url)
        r = self.woe_re.search(page)
        
        if not r:
            return None
        
        d = r.groupdict()
        return d['woeid']
    
    def getWeather(self, woeid):
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
        
        return "Weather for %s: %s and %s degrees" % (str_location, condition['current_condition'], condition['current_temp'])
        
        
        