#!/usr/bin/python

from BeautifulSoup import BeautifulSoup
import urllib2
import sys
import re

__author__ = "Anthony Casagrande <birdapi@gmail.com>"
__version__ = "0.7"

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

    def __repr__(self):
        return repr([self.name, self.link, self.description, self.thumb, self.cached, self.page, self.index])
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
       
    def __repr__(self):
        return repr([self.value, self.unit, self.expr, self.result, self.fullstring])
        
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
                if a["href"].find("calculator") != -1:
                    h2 = topstuff.find("h2")
                    if h2:
                        return parse_calc_result(h2.text)
        return None    
 
 
def get_search_url(query, page = 0, per_page = 10):
    # note: num per page might not be supported by google anymore
    query = query.strip().replace(":", "%3A").replace("+", "%2B").replace("&", "%26").replace(" ", "+")
    return "http://www.google.com/search?hl=en&q=%s&start=%i&num=%i" % (query, page * per_page, per_page)

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
                    result.unit = result.unit + token
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
    print "__main__"
    print Google.calculate("157.3kg in grams")
    print Google.calculate("cos(25 pi) / 17.4")
    print "\n\n"
    results = Google.search("wikipedia")
    for result in results:
        print result, "\n"
        
if __name__ == "__main__":
    main()