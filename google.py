#!/usr/bin/python

from BeautifulSoup import BeautifulSoup
import urllib2
import sys
import re

__author__ = "Anthony Casagrande <birdapi@gmail.com>"
__version__ = "0.1"

"""
Represents a standard google search result
"""
class GoogleResult:
    def __init__(self):
        self.name = None
        self.link = None
        self.description = None
        self.thumb = None
        slef.cached = None
        self.index = None

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
    def search(query):
        return None
    
    """
    Attempts to use google calculator to calculate the result of expr
    """
    @staticmethod
    def calculate(expr):
        return None

def main():
    print "__main__"
        
if __name__ == "__main__":
    main()