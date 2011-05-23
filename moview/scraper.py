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

#Remember about Beautifulsoup downgrade!

import mechanize
import time
import re
from urlparse import urlparse
import urllib2
from BeautifulSoup import BeautifulSoup

class MovieDataScraper(object):
    # Defines stagging time between requests pointed to the same service
    request_stagger = 2
    scraping_cache = {}
    scraping_domains = {}

    @classmethod
    def fetch(cls, url):
        now = time.time()
        key = url
        advert = False
        if cls.scraping_cache.has_key(key):
            print "Debug - getting from cache"
            data, cached_at, advert_avoided = cls.scraping_cache[key]
            return data
        domain = urlparse(url)[1]
#        domain = "www.onet.pl"
        print "Debug - domain: %s " % (domain)
        if cls.scraping_domains.has_key(domain):
            last_scraped = cls.scraping_domains[domain]
            print last_scraped
            elapsed = now - last_scraped
            print elapsed
            if elapsed < cls.request_stagger:
                wait_period = cls.request_stagger - elapsed
                print "Debug - need to wait"
                time.sleep(wait_period)
        else: #advert!
            advert = True
        cls.scraping_domains[domain] = time.time()
        request = mechanize.Request(url)
        response = mechanize.urlopen(request)
        if advert == True:
            time.sleep(cls.request_stagger)
            print "Avoid advert"
            response = mechanize.urlopen(request)
        data = response.read()
        cls.scraping_cache[key] = (data, now, True)
        return data

    def scrap(cls):
        raise NotImplementedError

class FilmwebScraper(MovieDataScraper):
#class FilmwebScraper(object):

    def __init__(self):
        super(FilmwebScraper, self).__init__()
        self.title = None
        self.year = None
        self.genres = []
        self.description = None
        self.votes = None
        self.rating = None

    def scrap(self, title, year):
        title = urllib2.quote(title)
        query = "http://www.filmweb.pl/search/film?q=" + title
        query += "&startYear=" + year + "&endYear=" + year
        query += "&startRate=&endRate=&startCount=&endCount=&sort=TEXT_SCORE&sortAscending=false"
        result = self.fetch(query)
        soup = BeautifulSoup(result)
        try:
            title_link = soup.find(True, {'class': 'searchResultTitle'})['href']
            print title_link
        except:
            return False
        query = "http://www.filmweb.pl" + title_link
        print "query %s" % (query)
        result = self.fetch(query)
        soup = BeautifulSoup(result)
        print soup.title.string

        self.title = title
        self.year = year

        description = soup.find(True, {'class': 'filmDescrBg', 'property': 'v:summary'})

        if description:
            self.description = description.next

        genres_tmp = soup.find(text="gatunek:")
        print genres_tmp
        if genres_tmp:
            for element in genres_tmp.next:
                self.genres.append(element.string)

        votes = soup.find(True, {'property': 'v:votes'}).string
        if votes:
            self.votes = votes

        rating = soup.find(True, {'property': 'v:average'}).string
        if rating:
            self.rating = rating

        return True

#t = MovieInfoScraper()
#print t.fetch("http://www.filmweb.pl")



