from babelpr.commands import ExplicitCommand
from babelpr import Message
from babelpr.chatbot import ChatBot
from babelpr.utils import stripHTML, getWebpage
import re
import urllib

class ReviewCommand(ExplicitCommand):
    
    def __init__(self, chatbot):
        ExplicitCommand.__init__(self, chatbot)
        
        self.name = "review"
        self.triggers = ["review"]
        self.description = "Gives you a review for a movie (from rottentomatoes.com)."
        self.syntax = "#review movie"

    def processCommand(self, message, trigger, arguments):
        assert isinstance(message, Message.Message)
        assert isinstance(self._chatbot, ChatBot)

        args = arguments.strip()
        if args == "":
            return "You must provide a movie name to get a review for."
        else:
            rotten = getWebpage("http://www.rottentomatoes.com/search/search.php?searchby=movies&search=%s" % urllib.quote(args))
            rotten = rotten.replace("\n","").replace("\r","")
            
            if rotten.find("Search Results for :") > -1:
                rotten_regex0 = '<ul id="movie_results_ul".*?<a target="_top" href="/m/(?P<url>[^"]+)'
                #rotten_regex0 = '<ul id="movie_results_ul".*?<a target="_top" href="/m/(?P<url>[^"]+)[^>]+>(?P<movie_name>[^<]+)</a>'
                redirect = re.findall(rotten_regex0, rotten, re.MULTILINE)
                if len(redirect) >= 1:
                    rotten = getWebpage("http://www.rottentomatoes.com/m/%s/" % redirect[0])
                    rotten = rotten.replace("\n","").replace("\r","")
            
            rotten_regex1 = """<span itemprop="ratingValue" id="all-critics-meter" class="meter certified numeric ">(\d+)</span>"""
            review = re.findall(rotten_regex1, rotten, re.MULTILINE)
            if len(review) != 1:
                found_freshness = False
                freshness = ""
            else:
                found_freshness = True
                freshness = review[0]
            rotten_regex2 = """Average Rating: <span>([^<]+)</span><br />"""
            review = re.findall(rotten_regex2, rotten, re.MULTILINE)
            if len(review) > 0:
                found_avg_rating = True
                avg_rating = review[0]
            else:
                found_avg_rating = False
                avg_rating = ""
            
            
            
            rotten_regexReview = """<p class="critic_consensus">(.+?)</p>"""
            review = re.findall(rotten_regexReview, rotten, re.MULTILINE)
            if len(review) > 0:
                found_critic_consensus = True
                critic_consensus = review[0]
            else:
                found_critic_consensus = False
                critic_consensus = ""
    
            if found_freshness or found_avg_rating:
                rotten_regex3 = """<title>([^<]+) - Rotten Tomatoes</title>"""
                review = re.findall(rotten_regex3, rotten, re.MULTILINE)
                if len(review) != 1:
                    movie_title = args
                else:
                    movie_title = review[0].split(" - ")[0]
                response = ""
                if found_freshness and found_avg_rating:
                    response += "'%s' recieved a freshness score of %s%% from rottentomatos.com with an average rating of %s." % (movie_title, freshness, avg_rating.strip())
                elif found_avg_rating:
                    response += "'%s' recieved an average rating of %s." % (movie_title, avg_rating.strip())
                elif found_freshness:
                    response += "'%s' recieved a freshness score of %s%% from rottentomatos.com." % (movie_title, freshness)
                    
                
                if found_critic_consensus:
                    if len(response) > 0:
                        response = response + "\n"
                    response = response + "\"%s\"" % (stripHTML(critic_consensus))
                    
                return response
                
            else:
                return "I haven't seen '%s'." % args