from babelpr.commands import ExplicitCommand
from babelpr import Message
from babelpr.chatbot import ChatBot
from babelpr.utils import getWebpage
import re
import random
import json


class AbamCommand(ExplicitCommand):
    
    def __init__(self, chatbot):
        ExplicitCommand.__init__(self, chatbot)
        
        self.triggers = ['abam','randomitems']
        self.name = 'abam'
        self.description = "Gives you a random set of items for all blind all mid"
        self.syntax = "#abam"
        
        self.boots = []
        self.non_boots = []
        self.item_blacklist = []
        
        self.loadItems('http://ddragon.leagueoflegends.com/cdn/0.301.3/data/en_US/item.json')
        
        

    def processCommand(self, message, trigger, arguments):
        assert isinstance(message, Message.Message)
        assert isinstance(self._chatbot, ChatBot)
        
        if len(self.boots) < 1 or len(self.non_boots) < 5:
            return "Items did not load correctly, sorry."
        
        items = []
        items.append(self.getRandom(self.boots))
        for i in range(1,6):
            item = None
            while item is None or item in items:
                item = self.getRandom(self.non_boots)
            items.append(item)
            
        
        ret = "Pick a champion, and buy only %s and %s" % (", ".join(items[0:-1]), items[-1])
        
        return ret
    
    def loadItems(self,  url):
        self.boots = []
        self.non_boots = []
        
        json_string = getWebpage(url)
        data = json.loads(json_string)
        items = data["data"]
        
        # hardcoded (yolo) list of items not usable in ABAM
        # this is probably because they are not allowed in that game/map type
        self.item_blacklist = [
            "The Lightbringer",
            "Wriggle's Lantern",
            "Spirit of the Ancient Golem",
            "Spirit of the Elder Lizard",
            "Spirit of the Spectral Wraith",
            "Ruby Sightstone",
            "Ohmwrecker",
            "The Bloodthirster",
            "Blackfire Torch",
            "Grez's Spectral Lantern",
            "Odyn's Veil",
            "game_item_displayname_2051",
            "Sword of the Occult",
            "Mejai's Soulstealer",
            "Guardian Angel",
            "Overlord's Bloodmail",
            "Wooglet's Witchcap"
        ]
    
        for item in items.itervalues():
            if item["name"] in self.item_blacklist:
                continue
            
            if "Enchantment: " in item["name"] or "Augment: " in item["name"]:
                continue

            if "Boots" in item["tags"] and "from" in item and len(item["from"]) > 0:
                self.boots.append(item["name"])
                continue
            
            if "Boots" not in item["tags"] and "from" in item and len(item["from"]) > 0 and "into" in item and len(item["into"]) == 0:
                self.non_boots.append(item["name"])
                continue
        
    
    def getRandom(self, items):
        i = random.randint(0,len(items)-1)
        return items[i]
