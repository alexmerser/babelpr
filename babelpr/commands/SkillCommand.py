from babelpr.commands import ExplicitCommand
from babelpr import Message
from babelpr.chatbot import ChatBot
from babelpr.utils import getWebpage
from bs4 import BeautifulSoup

import re


class SkillCommand(ExplicitCommand):
    
    def __init__(self, chatbot):
        ExplicitCommand.__init__(self, chatbot)
        
        self.triggers = ['skill']
        self.name = 'skill'
        self.description = "Returns information about a LoL champion skill"
        self.syntax = "#skill CHAMPION,{PASSIVE,Q,W,E,R}"
        
        self.skill_map = {
          'PASSIVE': 'skill_innate',
          'INNATE': 'skill_innate',
          'Q': 'skill_q',
          'W': 'skill_w',
          'E': 'skill_e',
          'R': 'skill_r'
        }
        

    def processCommand(self, message, trigger, arguments):
        assert isinstance(message, Message.Message)
        assert isinstance(self._chatbot, ChatBot)
        
        arguments = arguments.strip()
        arg_parts = arguments.split(',')
        if len(arg_parts) != 2:
            return "Syntax: " + self.syntax
        
        skill = arg_parts[1].strip().upper()
        if not skill in self.skill_map:
            return "Unknown skill label '%s'.  Please specify passive, Q, W, E, or R" % skill
        class_name = self.skill_map[skill]
        
        champion_name = self.getWikiaChampName(arg_parts[0].strip())
        if champion_name is None :
            return "Unknown champion: " + arg_parts[0] 
        
        
        
        url = "http://leagueoflegends.wikia.com/wiki/"+champion_name
        data = getWebpage(url)
        soup = BeautifulSoup(data)
        
        champname_span = soup.select('#champion_info span:first')
        
        if not champname_span or len(champname_span) == 0:
            return "Sorry, I couldn't find info for champion '%s'" % champion_name
        
        formatted_champ_name = champname_span[0].string
        
        skill_div = soup.select('div.'+class_name)
        if not skill_div or len(skill_div) == 0:
            return "Sorry, I couldn't find info on skill '%s' for %s" % (skill, formatted_champ_name)
        
        skill_soup = skill_div[0]
        
        try:
            skill_name = self.requiredSelect(skill_soup, '.skill_header > span').string
            cooldown_cost = self.flatten(self.requiredSelect(skill_soup, '.skill_header > ul'))
            cooldown_cost = re.sub("(\s)(\w+):", r',\1\2', cooldown_cost)
            
            sub_section = skill_soup.select('.skill_wrapper > div')[1]
            skill_text = self.flatten(self.requiredSelect(sub_section, 'div'))
            skill_leveling = self.flatten(self.requiredSelect(sub_section, 'div.skill_leveling'))
        except:
            return "Sorry, I couldn't parse the info on skill '%s' for %s" % (skill, formatted_champ_name)
            
        
        ret = "%s (%s) for %s:\n%s\n%s\n%s" % (skill_name, skill, formatted_champ_name, cooldown_cost, skill_text, skill_leveling) 
        re.sub("\n\n+" , "\n", ret)
        return ret
    
    def flatten(self, elements):
        s = " ".join(elements.findAll(text=True))
        s = s.replace(u'\xa0', ' ')        
        s = s.replace(u'\xc2', ' ')
        return re.sub("\s\s+" , " ", s)
    
    def requiredSelect(self, soup, selector):
        match = soup.select(selector)
        if not match or len(match) == 0:
            raise Exception("requried selector not found: " + selector)
        return match[0]
    
    def getWikiaChampName(self, champ_name):
        return champ_name