#!/usr/bin/python

from BeautifulSoup import BeautifulSoup
import urllib2
import sys
import re

__author__ = "Anthony Casagrande <birdapi@gmail.com>"
__version__ = "0.3"

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
       
    def __repr__(self):
        return "%s %s" % (self.value, self.unit)
        
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
            url = Google.get_search_url(query, i)
            try:
                request = urllib2.Request(url)
                request.add_header("User-Agent", "Mozilla/5.001 (windows; U; NT4.0; en-US; rv:1.0) Gecko/25250101")
                html = urllib2.urlopen(request).read()
            except:
                print "Error accessing:", url
                break
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
        return None
        
    @staticmethod    
    def get_search_url(query, page = 0, per_page = 10):
        # note: num per page might not be supported by google anymore
        query = query.strip().replace(":", "%3A").replace("+", "%2B").replace("&", "%26").replace(" ", "+")
        return "http://www.google.com/search?hl=en&q=%s&start=%i&num=%i" % (query, page * per_page, per_page)

def main():
    print "__main__"
    results = Google.search("testing, testing, 123")
    for result in results:
        print result, "\n"
        
if __name__ == "__main__":
    main()