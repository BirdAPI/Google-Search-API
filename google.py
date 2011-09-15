#!/usr/bin/python

from BeautifulSoup import BeautifulSoup
from pprint import pprint
import os
import threading
import urllib
import urllib2
import sys
import re

__author__ = "Anthony Casagrande <birdapi@gmail.com>"
__version__ = "0.8"

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

"""
Represents a google image search result
"""
class ImageResult:  
    def __init__(self):
        self.name = None
        self.link = None
        self.thumb = None
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
    Attempts to use google calculator to calculate the result of expr
    """
    @staticmethod
    def calculate(expr):
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
    def search_images(query, image_options = None, pages = 1):
        results = []
        for i in range(pages):
            url = get_image_search_url(query, image_options, i)
            html = get_html(url)
            if html:
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
 
def get_search_url(query, page = 0, per_page = 10):
    # note: num per page might not be supported by google anymore (because of google instant)
    query = query.strip().replace(":", "%3A").replace("+", "%2B").replace("&", "%26").replace(" ", "+")
    return "http://www.google.com/search?hl=en&q=%s&start=%i&num=%i" % (query, page * per_page, per_page)

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
        
def main():
    pprint(vars(Google.calculate("157.3kg in grams")))
    print ""
    pprint(vars(Google.calculate("cos(25 pi) / 17.4")))
    print "\n\n"
    options = ImageOptions()
    options.image_type = ImageType.CLIPART
    options.larger_than = LargerThan.MP_4
    options.color = "green"
    results = Google.search_images("banana", options)
    for result in results:
        pprint(vars(result))
        print "\n\n"
        
if __name__ == "__main__":
    main()
    