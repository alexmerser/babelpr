import sgmllib
import socket
import urllib2
import cookielib
import os
import urllib


def stripHTML(html_string):
    stripper = Stripper()
    html_string = html_string.replace("&#39;","'").replace("&quot;","\"").replace("&lt;","<").replace("&gt;",">").replace("<br />"," ").replace("\n","").replace("\r","").replace("\t"," ")
    return stripper.strip(html_string)

def getWebpage(url, txdata=None):
    timeout = 10
    socket.setdefaulttimeout(timeout)
    #user_agent = "Mozilla/5.0 Gecko/20070219 Firefox/2.0.0.2"
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1309.0 Safari/537.17"
    COOKIEFILE = 'cookies.lwp'
    urlopen = urllib2.urlopen
    cj = cookielib.LWPCookieJar()
    Request = urllib2.Request
    if os.path.isfile(COOKIEFILE):
        cj.load(COOKIEFILE)
    if cookielib:
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(opener)

    txheaders =  {'User-agent' : user_agent}
    if not txdata is None:
        txdata = urllib.urlencode(txdata)
    try:
        req = Request(url, txdata, txheaders)
        handle = urlopen(req)
        result = handle.read()
    except:
        result = ""
        
    #debug_log(0,"Debug",result)
    cj.save(COOKIEFILE)
    return result

class Stripper(sgmllib.SGMLParser):
        def __init__(self):
                sgmllib.SGMLParser.__init__(self)
                
        def strip(self, some_html):
                self.theString = ""
                self.feed(some_html)
                self.close()
                return self.theString
                
        def handle_data(self, data):
                self.theString += data