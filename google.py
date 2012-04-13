#!/usr/bin/python

from BeautifulSoup import BeautifulSoup
from pprint import pprint
import os
import threading
import httplib
import urllib
import urllib2
import sys
import re
try:
    import json
except ImportError:
    import simplejson as json

__author__ = "Anthony Casagrande <birdapi@gmail.com>"
__version__ = "0.9"

"""
Represents a standard google search result
"""
class GoogleResult:
    def __init__(self):
        self.name = None
        self.link = None
        self.description = None
        self.thumb = None
        self.cached = None
        self.page = None
        self.index = None
        
"""
Represents a result returned from google calculator
"""        
class CalculatorResult:
    def __init__(self):
        self.value = None
        self.unit = None
        self.expr = None
        self.result = None
        self.fullstring = None

class ShoppingResult:
    def __init__(self):
        self.name = None
        self.link = None
        self.thumb = None
        self.subtext = None
        self.description = None
        self.compare_url = None
        self.store_count = None
        self.min_price = None

"""
Represents a google image search result
"""
class ImageResult:  
    def __init__(self):
        self.name = None
        self.link = None
        self.thumb = None
        self.thumb_width = None
        self.thumb_height = None
        self.width = None
        self.height = None
        self.filesize = None
        self.format = None
        self.domain = None
        self.page = None
        self.index = None
        
class ImageOptions:
    def __init__(self):
        self.image_type = None
        self.size_category = None
        self.larger_than = None
        self.exact_width = None
        self.exact_height = None
        self.color_type = None
        self.color = None
        
    def get_tbs(self):
        tbs = None
        if self.image_type:
            # clipart
            tbs = add_to_tbs(tbs, "itp", self.image_type)
        if self.size_category and not (self.larger_than or (self.exact_width and self.exact_height)): 
            # i = icon, l = large, m = medium, lt = larger than, ex = exact
            tbs = add_to_tbs(tbs, "isz", self.size_category)
        if self.larger_than:   
            # qsvga,4mp
            tbs = add_to_tbs(tbs, "isz", SizeCategory.LARGER_THAN)
            tbs = add_to_tbs(tbs, "islt", self.larger_than)
        if self.exact_width and self.exact_height:
            tbs = add_to_tbs(tbs, "isz", SizeCategory.EXACTLY)
            tbs = add_to_tbs(tbs, "iszw", self.exact_width)
            tbs = add_to_tbs(tbs, "iszh", self.exact_height)
        if self.color_type and not self.color:
            # color = color, gray = black and white, specific = user defined
            tbs = add_to_tbs(tbs, "ic", self.color_type)
        if self.color:
            tbs = add_to_tbs(tbs, "ic", ColorType.SPECIFIC)
            tbs = add_to_tbs(tbs, "isc", self.color)
        return tbs
        
"""
Defines the public static api methods
"""
class Google:
    DEBUG_MODE = False

    """
    Returns a list of GoogleResult
    """
    @staticmethod
    def search(query, pages = 1):
        results = []
        for i in range(pages):
            url = get_search_url(query, i)
            html = get_html(url)
            if html:
                if Google.DEBUG_MODE:
                    write_html_to_file(html, "{0}_{1}.html".format(query.replace(" ", "_"), i))
                soup = BeautifulSoup(html)
                lis = soup.findAll("li", attrs = { "class" : "g" })
                j = 0
                for li in lis:
                    res = GoogleResult()
                    res.page = i
                    res.index = j
                    a = li.find("a")
                    res.name = a.text.strip()
                    res.link = a["href"]
                    if res.link.startswith("/search?"):
                        # this is not an external link, so skip it
                        continue
                    sdiv = li.find("div", attrs = { "class" : "s" })
                    if sdiv:
                        res.description = sdiv.text.strip()
                    results.append(res)
                    j = j + 1
        return results
    
    """
    OLD WAY OF DOING THIS. Attempts to use google calculator to calculate the result of expr
    """
    @staticmethod
    def calculate_old(expr):
        url = get_search_url(expr)
        html = get_html(url)
        if html:
            soup = BeautifulSoup(html)
            topstuff = soup.find("div", id="topstuff")
            if topstuff:
                a = topstuff.find("a")
                if a and a["href"].find("calculator") != -1:
                    h2 = topstuff.find("h2")
                    if h2:
                        return parse_calc_result(h2.text)
        return None 

    @staticmethod
    def search_images_old(query, image_options = None, pages = 1):
        results = []
        for i in range(pages):
            url = get_image_search_url(query, image_options, i)
            html = get_html(url)
            if html:
                if Google.DEBUG_MODE:
                    write_html_to_file(html, "images_{0}_{1}.html".format(query.replace(" ", "_"), i))
                j = 0
                soup = BeautifulSoup(html)
                match = re.search("dyn.setResults\((.+)\);</script>", html)
                if match:
                    init = unicode(match.group(1), errors="ignore")
                    tokens = init.split('],[')
                    for token in tokens:
                        res = ImageResult()
                        res.page = i
                        res.index = j
                        toks = token.split(",")
                        
                        # should be 32 or 33, but seems to change, so just make sure no exceptions
                        # will be thrown by the indexing
                        if (len(toks) > 22):
                            for t in range(len(toks)):
                                toks[t] = toks[t].replace('\\x3cb\\x3e','').replace('\\x3c/b\\x3e','').replace('\\x3d','=').replace('\\x26','&')
                            match = re.search("imgurl=(?P<link>[^&]+)&imgrefurl", toks[0])
                            if match:
                                res.link = match.group("link")
                            res.name = toks[6].replace('"', '')
                            res.thumb = toks[21].replace('"', '')
                            res.format = toks[10].replace('"', '')
                            res.domain = toks[11].replace('"', '')
                            match = re.search("(?P<width>[0-9]+) &times; (?P<height>[0-9]+) - (?P<size>[^ ]+)", toks[9].replace('"', ''))
                            if match:
                                res.width = match.group("width")
                                res.height = match.group("height")
                                res.filesize = match.group("size")        
                            results.append(res)
                            j = j + 1
        return results
    
    @staticmethod
    def search_images(query, image_options = None, pages = 1):
        results = []
        for i in range(pages):
            url = get_image_search_url(query, image_options, i)
            html = get_html(url)
            if html:
                if Google.DEBUG_MODE:
                    write_html_to_file(html, "images_{0}_{1}.html".format(query.replace(" ", "_"), i))
                soup = BeautifulSoup(html)
                j = 0
                tds = soup.findAll("td")
                for td in tds:
                    a = td.find("a")
                    if a and a["href"].find("imgurl") != -1:
                        res = ImageResult()
                        res.page = i
                        res.index = j
                        tokens = a["href"].split("&")
                        match = re.search("imgurl=(?P<link>[^&]+)", tokens[0])
                        if match:
                            res.link = match.group("link")
                            res.format = res.link[res.link.rfind(".") + 1:]
                        img = td.find("img")
                        if img:
                            res.thumb = img["src"]
                            res.thumb_width = img["width"]
                            res.thumb_height = img["height"]
                        match = re.search("(?P<width>[0-9]+) &times; (?P<height>[0-9]+) - (?P<size>[^&]+)", td.text)
                        if match:
                            res.width = match.group("width")
                            res.name = td.text[:td.text.find(res.width)]
                            res.height = match.group("height")
                            res.filesize = match.group("size")
                        cite = td.find("cite")
                        if cite:
                            res.domain = cite["title"]
                        results.append(res)
                        j = j + 1
        return results
    
    @staticmethod
    def shopping(query, pages=1):
        results = []
        for i in range(pages):
            url = get_shopping_url(query, i)
            html = get_html(url)
            if html:
                if Google.DEBUG_MODE:
                    write_html_to_file(html, "shopping_{0}_{1}.html".format(query.replace(" ", "_"), i))
                j = 0
                soup = BeautifulSoup(html)
                
                products = soup.findAll("li", "g")
                for prod in products:
                    res = ShoppingResult()
                    
                    divs = prod.findAll("div")
                    for div in divs:
                        match = re.search("from (?P<count>[0-9]+) stores", div.text.strip())
                        if match:
                            res.store_count = match.group("count")
                            break
                    
                    h3 = prod.find("h3", "r")
                    if h3:
                        a = h3.find("a")
                        if a:
                            res.compare_url = a["href"]
                        res.name = h3.text.strip()
                    
                    psliimg = prod.find("div", "psliimg")
                    if psliimg:
                        img = psliimg.find("img")
                        if img:
                            res.thumb = img["src"]
                    
                    f = prod.find("div", "f")
                    if f:
                        res.subtext = f.text.strip()
                        
                    price = prod.find("div", "psliprice")
                    if price:
                        res.min_price = price.text.strip()
                    
                    results.append(res)
                    j = j + 1
        return results
    
    """
    Converts one currency to another.
    [amount] from_curreny = [return_value] to_currency
    """
    @staticmethod
    def convert_currency(amount, from_currency, to_currency):
        if from_currency == to_currency:
            return 1.0
        conn = httplib.HTTPSConnection("www.google.com")
        req_url = "/ig/calculator?hl=en&q={0}{1}=?{2}".format(amount, from_currency.replace(" ", "%20"), to_currency.replace(" ", "%20"))
        headers = { "User-Agent": "Mozilla/5.001 (windows; U; NT4.0; en-US; rv:1.0) Gecko/25250101" }
        conn.request("GET", req_url, "", headers)
        response = conn.getresponse()
        rval = response.read().decode("utf-8").replace(u"\xa0", "")
        conn.close()
        rhs = rval.split(",")[1].strip()
        s = rhs[rhs.find('"')+1:]
        rate = s[:s.find(" ")]
        return float(rate)
        
    """
    Gets the exchange rate of one currency to another.
    1 from_curreny = [return_value] to_currency
    """
    @staticmethod
    def exchange_rate(from_currency, to_currency):
        return Google.convert_currency(1, from_currency, to_currency)
 
    """
    Attempts to use google calculator to calculate the result of expr
    """
    @staticmethod
    def calculate(expr):
        conn = httplib.HTTPSConnection("www.google.com")
        req_url = "/ig/calculator?hl=en&q={0}".format(expr.replace(" ", "%20"))
        headers = { "User-Agent": "Mozilla/5.001 (windows; U; NT4.0; en-US; rv:1.0) Gecko/25250101" }
        conn.request("GET", req_url, "", headers)
        response = conn.getresponse()
        j = response.read().decode("utf-8").replace(u"\xa0", "")
        conn.close()
        j = re.sub(r"{\s*'?(\w)", r'{"\1', j)
        j = re.sub(r",\s*'?(\w)", r',"\1', j)
        j = re.sub(r"(\w)'?\s*:", r'\1":', j)
        j = re.sub(r":\s*'(\w)'\s*([,}])", r':"\1"\2', j)
        js = json.loads(j)
        return parse_calc_result(js["lhs"] + " = " + js["rhs"])
 
def normalize_query(query):
    return query.strip().replace(":", "%3A").replace("+", "%2B").replace("&", "%26").replace(" ", "+")
 
def get_search_url(query, page = 0, per_page = 10):
    # note: num per page might not be supported by google anymore (because of google instant)
    return "http://www.google.com/search?hl=en&q=%s&start=%i&num=%i" % (normalize_query(query), page * per_page, per_page)

def get_shopping_url(query, page=0, per_page=10):
    return "http://www.google.com/search?hl=en&q={0}&tbm=shop&start={1}&num={2}".format(normalize_query(query), page * per_page, per_page)
    
class ImageType:
    NONE = None
    FACE = "face"
    PHOTO = "photo"
    CLIPART = "clipart"
    LINE_DRAWING = "lineart"
    
class SizeCategory:
    NONE = None
    ICON = "i"
    LARGE = "l"
    MEDIUM = "m"
    SMALL = "s"
    LARGER_THAN = "lt"
    EXACTLY = "ex"
    
class LargerThan:
    NONE = None
    QSVGA = "qsvga" # 400 x 300
    VGA = "vga"     # 640 x 480
    SVGA = "svga"   # 800 x 600
    XGA = "xga"     # 1024 x 768
    MP_2 = "2mp"    # 2 MP (1600 x 1200)
    MP_4 = "4mp"    # 4 MP (2272 x 1704)
    MP_6 = "6mp"    # 6 MP (2816 x 2112)
    MP_8 = "8mp"    # 8 MP (3264 x 2448)
    MP_10 = "10mp"  # 10 MP (3648 x 2736)
    MP_12 = "12mp"  # 12 MP (4096 x 3072)
    MP_15 = "15mp"  # 15 MP (4480 x 3360)
    MP_20 = "20mp"  # 20 MP (5120 x 3840)
    MP_40 = "40mp"  # 40 MP (7216 x 5412)
    MP_70 = "70mp"  # 70 MP (9600 x 7200)

class ColorType:
    NONE = None
    COLOR = "color"
    BLACK_WHITE = "gray"
    SPECIFIC = "specific"
    
def get_image_search_url(query, image_options=None, page=0, per_page=20):
    query = query.strip().replace(":", "%3A").replace("+", "%2B").replace("&", "%26").replace(" ", "+")
    url = "http://images.google.com/images?q=%s&sa=N&start=%i&ndsp=%i&sout=1" % (query, page * per_page, per_page)
    if image_options:
        tbs = image_options.get_tbs()
        if tbs:
            url = url + tbs
    return url
    
def add_to_tbs(tbs, name, value):
    if tbs:
        return "%s,%s:%s" % (tbs, name, value)
    else:
        return "&tbs=%s:%s" % (name, value) 
    
def parse_calc_result(string):
    result = CalculatorResult()
    result.fullstring = string
    string = string.strip().replace(u"\xa0", " ")
    if string.find("=") != -1:
        result.expr = string[:string.rfind("=")].strip()
        string = string[string.rfind("=") + 2:]
        result.result = string
    tokens = string.split(" ")
    if len(tokens) > 0:
        result.value = ""
        for token in tokens:
            if is_number(token):
                result.value = result.value + token
            else:
                if result.unit:
                    result.unit = result.unit + " " + token
                else:
                    result.unit = token
        return result
    return None
        
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
    
def get_html(url):
    try:
        request = urllib2.Request(url)
        request.add_header("User-Agent", "Mozilla/5.001 (windows; U; NT4.0; en-US; rv:1.0) Gecko/25250101")
        html = urllib2.urlopen(request).read()
        return html
    except:
        print "Error accessing:", url
        return None        

def write_html_to_file(html, filename):
    of = open(filename, "w")
    of.write(html)
    of.flush()
    of.close()
        
def test():
    search = Google.search("github")
    if search is None or len(search) == 0: 
        print "ERROR: No Search Results!"
    else: 
        print "PASSED: {0} Search Results".format(len(search))
    
    shop = Google.shopping("Disgaea 4")
    if shop is None or len(shop) == 0: 
        print "ERROR: No Shopping Results!"
    else: 
        print "PASSED: {0} Shopping Results".format(len(shop))
    
    options = ImageOptions()
    options.image_type = ImageType.CLIPART
    options.larger_than = LargerThan.MP_4
    options.color = "green"
    images = Google.search_images("banana", options)
    if images is None or len(images) == 0: 
        print "ERROR: No Image Results!"
    else:
        print "PASSED: {0} Image Results".format(len(images))
        
    calc = Google.calculate("157.3kg in grams")
    if calc is not None and int(calc.value) == 157300:
        print "PASSED: Calculator passed"
    else:
        print "ERROR: Calculator failed!"
        
    euros = Google.convert_currency(5.0, "USD", "EUR")
    if euros is not None and euros > 0.0:
        print "PASSED: Currency convert passed"
    else:
        print "ERROR: Currency convert failed!"
        
def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--debug":
        Google.DEBUG_MODE = True
        print "DEBUG_MODE ENABLED"
    test()
        
if __name__ == "__main__":
    main()
    