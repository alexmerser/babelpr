import json
from babelpr.chatbot import ChatBot
from babelpr.globals import BabelGlobals
import os
import traceback
import sys
import logging

def run():
    # build a path to the config file
    config_file = os.path.join(BabelGlobals.location, 'config.json')
    
    # attempt to load the config
    try:
        f = open(config_file, 'r')
        config = json.load(f)
    except ValueError:
        print "Unable to parse config - please ensure config.json exists and is valid"
        return
    
    # set the logging level
    level = logging.INFO
    
    if(config.has_key('LoggingLevel')):
        level = logging.DEBUG
    logging.basicConfig(level=level, format='%(levelname)-8s %(message)s')        
    
    # initialize and start the ChatBot
    try:
        client = ChatBot(config)
        client.start()
    except:
        logging.exception("Exception in ChatBot")
        os._exit(1)
    
# save the directory from which this script resides in
BabelGlobals.location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

if __name__ == "__main__":
    # hand off to the run method
    run()