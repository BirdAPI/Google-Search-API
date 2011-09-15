Google Search API
=====

Google Search API is a python based library for searching various functionalities of google.  It uses screen scraping to retrieve the results, and thus is unreliable if the way google's web pages are returned change in the future.

*Disclaimer: This software uses screen scraping to retreive search results from google.com, and therefore this software may stop working at any given time.  Use this software at your own risk. I assume no responsibility for how this software API is used by others.*

## Google Web Search
You can search google web in the following way:

`search_results = Google.search("This is my query")`

`search_results` will contain a list of GoogleResult objects

        GoogleResult:
            self.name # The title of the link
            self.link # The link url
            self.description # The description of the link
            self.thumb # The link to a thumbnail of the website (not implemented yet)
            self.cached # A link to the cached version of the page
            self.page # What page this result was on (When searching more than one page)
            self.index # What index on this page it was on


## Google Calculator



## Google Image Search


