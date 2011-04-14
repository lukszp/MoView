1# import mechanize
# request = mechanize.Request("http://example.com/")
# # note we're using the urlopen from mechanize, not urllib2
# response = mechanize.urlopen(request)
# # let's say this next request requires a cookie that was set
# # in response
# request2 = mechanize.Request("http://example.com/spam.html")
# response2 = mechanize.urlopen(request2)

# print response2.geturl()
# print response2.info()  # headers
# print response2.read()  # body (readline and readlines work too)

import mechanize
import time
import re
from urlparse import urlparse
from BeautifulSoup import BeautifulSoup

class MovieInfoScraper(object):
    def __init__(self, request_stagger = 2):
        self.request_stagger = request_stagger
        self.scraping_cache = {}
        self.scraping_domains = {}

    def fetch(self, url):
        now = time.time()
        key = url
        advert = False
        if self.scraping_cache.has_key(key):
            print "Debug - getting from cache"
            data, cached_at, advert_avoided = self.scraping_cache[key]
            return data
        domain = urlparse(url)[1]
#        domain = "www.onet.pl"
        print "Debug - domain: %s " % (domain)
        if self.scraping_domains.has_key(domain):
            last_scraped = self.scraping_domains[domain]
            print last_scraped
            elapsed = now - last_scraped
            print elapsed
            if elapsed < self.request_stagger:
                wait_period = self.request_stagger - elapsed
                print "Debug - need to wait"
                time.sleep(wait_period)
        else: #advert!
            advert = True
        self.scraping_domains[domain] = time.time()
        request = mechanize.Request(url)
        response = mechanize.urlopen(request)
        if advert == True:
            time.sleep(self.request_stagger)
            print "Avoid advert"
            response = mechanize.urlopen(request)
        data = response.read()
        self.scraping_cache[key] = (data, now, True)
        return data
        
        
    def filmweb_scraper(self, title, year):
        query = "http://www.filmweb.pl/search/film?q=" + title
        query += "&startYear=" + year + "&endYear=" + year
        query += "&startRate=&endRate=&startCount=&endCount=&sort=TEXT_SCORE&sortAscending=false"
        result = self.fetch(query)
        soup = BeautifulSoup(result)
        try:
            title_link = soup.find(True, {'class': 'searchResultTitle'})['href']
            print title_link
        except:
            return None
        query = "http://www.filmweb.pl" + title_link
        print "query %s" % (query)
        result = self.fetch(query)
        soup = BeautifulSoup(result)
        print soup.title
        #title = soup({'class' : 'searchResultTitle'}).b.string
        #print title
        results = {}
        description = soup.find(True, {'class': 'filmDescrBg', 'property': 'v:summary'})
        if description:
            results['description'] = description.string
        genres_tmp = soup.find(text="gatunek:").next
        genres = ""
        for element in genres_tmp:
            genres += element.string
        results['genres'] = genres
        results['votes'] = soup.find(True, {'property': 'v:votes'}).string
        results['rating'] = soup.find(True, {'property': 'v:average'}).string
        return results

#t = MovieInfoScraper()
#print t.fetch("http://www.filmweb.pl")



