import StringIO, cookielib, gzip, os, re, sgmllib, socket, urllib, urllib2, requests


def stripHTML(html_string):
    stripper = Stripper()
    html_string = html_string.replace("&#39;","'").replace("&quot;","\"").replace("&lt;","<").replace("&gt;",">").replace("<br />"," ").replace("\n","").replace("\r","").replace("\t"," ").replace("<br>"," ").replace("<br/>"," ")
    return stripper.strip(html_string)

def performRestApiGet(url):
    try:
        r = requests.get(url, timeout=5)
        status_code = r.status_code
        json = r.json()
    except ValueError:
        json = None
    except requests.exceptions.Timeout:
        status_code = 504
        json = None

    return status_code, json

def getWebpage(url, txdata=None):
    timeout = 5
    socket.setdefaulttimeout(timeout)
    COOKIEFILE = 'cookies.lwp'
    urlopen = urllib2.urlopen
    cj = cookielib.LWPCookieJar()
    Request = urllib2.Request
    if os.path.isfile(COOKIEFILE):
        cj.load(COOKIEFILE)
    if cookielib:
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(opener)

    txheaders =  {
      'Accept':"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
      'Accept-Encoding':"gzip,deflate,sdch",
      'Accept-Language':"en-US,en;q=0.8",
      'Cache-Control':"max-age=0",
      'Connection':"keep-alive",
      'User-agent' : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.32 Safari/537.36"
    }
    if not txdata is None:
        txdata = urllib.urlencode(txdata)
    try:
        req = Request(url, txdata, txheaders)
        handle = urlopen(req, None, timeout)
        
        if handle.info().get('Content-Encoding') == 'gzip':
            buf = StringIO.StringIO(handle.read())
            f = gzip.GzipFile(fileobj=buf)
            result = f.read()        
        else:
            result = handle.read()
    except urllib2.HTTPError, e:
        print e
        result = ""
    except Exception, e:
        print e
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
                
                
def getZipDistance(zip1, zip2):
    #make sure we have cookie data
    default_cookie_header = """#LWP-Cookies-2.0"""
    default_cookie_line = """Set-Cookie3: u="f=4&c=2&i=&n=&r=&d=6%2F20%2F2007&e=&l=U&s="; path="/"; domain=".melissadata.com"; path_spec; expires="2027-07-20 07:00:00Z"; version=0"""
    cookie_search = "domain=\".melissadata.com\""
    cookie_file = 'cookies.lwp'
    if os.path.isfile(cookie_file):
        fh = open(cookie_file,'r')
        cookiedata = fh.read()
        fh.close()
        if cookiedata.find(cookie_search) < 1:
            cookiedata = cookiedata + '\r\n' + default_cookie_line
            os.remove(cookie_file)
            fh = open(cookie_file,'w')
            fh.write(cookiedata)
            fh.close()
    else:
        fh = open(cookie_file,'w')
        fh.write(default_cookie_header + '\r\n')
        fh.write(default_cookie_line + '\r\n')
        fh.close()
    
    if isInt(zip1):
        zip1 = "%d" % int(zip1)
    if isInt(zip2):
        zip2 = "%d" % int(zip2)
        
    while len(zip1) < 5:
        zip1 = "0" + zip1
    while len(zip2) < 5:
        zip2 = "0" + zip2
    try:
        url = "http://www.melissadata.com/lookups/zipdistance.asp?zipcode1=%s&zipcode2=%s&submit1=Submit" % (urllib.quote(zip1),urllib.quote(zip2))
        zip_distance_page = getWebpage(url)
    except:
        zip_distance_page = ""
    zip_distance_regex = "Distance from .*? is <b>(?P<distance>[^<]+)</b>"
    zip_distance = re.findall(zip_distance_regex, zip_distance_page, re.MULTILINE)
    if len(zip_distance) > 0:
        zip_distance = zip_distance[0].strip()
    else:
        zip_distance = -1
    return zip_distance       

def isInt(s):
    valid_int = False
    try:
        i = int(s)
        valid_int = True
    except:
        valid_int = False
    return valid_int         

def PrettyRelativeTime(time_diff_secs):
    # Each tuple in the sequence gives the name of a unit, and the number of
    # previous units which go into it.
    weeks_per_month = 365.242 / 12 / 7
    intervals = [('minute', 60), ('hour', 60), ('day', 24), ('week', 7),
                 ('month', weeks_per_month), ('year', 12)]

    unit, number = 'second', abs(time_diff_secs)
    for new_unit, ratio in intervals:
        new_number = float(number) / ratio
        # If the new number is too small, don't go to the next unit.
        if new_number < 2:
            break
        unit, number = new_unit, new_number
    shown_num = int(number)
    return '{} {}'.format(shown_num, unit + ('' if shown_num == 1 else 's'))