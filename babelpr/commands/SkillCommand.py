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
          'PASSIVE': 0,
          'Q': 1,
          'W': 2,
          'E': 3,
          'R': 4
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
        skill_seq = self.skill_map[skill]
        
        champion_name = self.formatChampName(arg_parts[0].strip())
        if champion_name is None :
            return "Unknown champion: " + arg_parts[0] 
        
        
        
        url = "http://gameinfo.na.leagueoflegends.com/en/game-info/champions/"+champion_name+'/'
        data = getWebpage(url)
        soup = BeautifulSoup(data)
        
        champname_node = soup.select('#champ_header h1')
        
        if not champname_node or len(champname_node) == 0:
            return "Sorry, I couldn't find info for champion '%s'" % champion_name
        
        formatted_champ_name = champname_node[0].string
        
        passive_div = soup.select('#spell-passive')
        if not passive_div or len(passive_div) == 0:
            return "Sorry, I couldn't find info on skill '%s' for %s" % (skill, formatted_champ_name)

        skills_container = passive_div[0].parent.parent
        skill_nodes = skills_container.select(".section-wrapper-content-wrapper > div.gs-container")

        if not skill_nodes or len(skill_nodes) <= skill_seq:
            return "Sorry, I couldn't parse the info on skill '%s' for %s" % (skill, formatted_champ_name)
        
        try:
            skill_node = skill_nodes[skill_seq]
            skill_name = self.requiredSelect(skill_node, 'h3').string
            skill_des = self.flattenRequiredSelect(skill_node, 'p')
            skill_des = skill_des.replace("Range: ", " Range: ")
            skill_des = re.sub(r'\s{2,}', '\n', skill_des)
        except:
            return "Sorry, I couldn't parse the info on skill '%s' for %s" % (skill, formatted_champ_name)
            
        
        ret = "%s (%s) for %s:\n%s" % (skill_name, skill, formatted_champ_name, skill_des) 
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

    def flattenRequiredSelect(self, soup, selector):
        matches = soup.select(selector)
        if not matches or len(matches) == 0:
            raise Exception("requried selector not found: " + selector)
        
        text = ""
        for match in matches:
            text += self.flatten(match) + " "
        return text

    def formatChampName(self, champ_name):
        return champ_name.lower()