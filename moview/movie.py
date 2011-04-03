class Movie(object):
    #Store data about movie object.
    #Data is obtained from:
    #imdb.com


    def __init__(self):
        self.imdb_id = None
        self.path = None
        self.imdb_object = None
        self.title = None
        self.genres = None
        self.runtime = None
        self.language = None
        self.rating = None
        self.plot = None
        self.year = None

    def to_unicode_or_bust(self, obj, encoding='utf-8'):
        if isinstance(obj, basestring):
            if not isinstance(obj, unicode):
                obj = unicode(obj, encoding)
        return obj

    def prepare_data_from_imdb(self):
        keys = self.imdb_object.keys()
        self.path = self.to_unicode_or_bust(self.path)
        if 'title' in keys:
            self.title = ''.join(self.imdb_object['title'])
        if 'genres' in keys:
            self.genres = ' '.join(self.imdb_object['genres'])
        if 'runtimes' in keys:
            self.runtime = ' '.join(self.imdb_object['runtime'])
        if 'languages' in keys:
            self.language = ' '.join(self.imdb_object['language'])
        if 'rating' in keys:
            self.rating = self.imdb_object['rating']
        if 'plot' in keys:
            self.plot = ' '.join(self.imdb_object['plot'])
            self.plot = self.plot[:self.plot.find('::')]
