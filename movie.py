NO_IMDBID_FOUND = -1

class Movie(object):
    def __init__(self):
        self.IMDBID = NO_IMDBID_FOUND
        self.path = None
        self.imdbObject = None
        self.title = None
        self.genres = None
        self.runtime = None
        self.language = None
        self.rating = None
        self.plot = None
        
    def prepare_data_from_imdb(self):
        
        if (self.imdbObject.has_key('title')):
            self.title = ''.join(self.imdbObject['title'])
        if (self.imdbObject.has_key('genres')):
            self.genres = ' '.join(self.imdbObject['genres'])
        if (self.imdbObject.has_key('runtime')):
            self.runtime =  ' '.join(self.imdbObject['runtime'])
        if (self.imdbObject.has_key('language')):
            self.language = ' '.join(self.imdbObject['language'])
        if (self.imdbObject.has_key('rating')):
            self.rating = self.imdbObject['rating']
        if (self.imdbObject.has_key('plot')):
            self.plot = ' '.join(self.imdbObject['plot'])
