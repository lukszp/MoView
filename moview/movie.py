NO_IMDBID_FOUND = -1


class Movie(object):
    """
    Store data about movie object.
    Data is obtained from:
    imdb.com
    """


    def __init__(self):
        self.imdb_id = NO_IMDBID_FOUND
        self.path = None
        self.imdb_object = None
        self.title = None
        self.genres = None
        self.runtime = None
        self.language = None
        self.rating = None
        self.plot = None

    def to_unicode_or_bust(self, obj, encoding='utf-8'):
        if isinstance(obj, basestring):
            if not isinstance(obj, unicode):
                obj = unicode(obj, encoding)
        return obj

    def prepare_data_from_imdb(self):
        keys = self.imdb_object.keys()
        self.path = self.to_unicode_or_bust(self.path)
        if 'title' in keys:
            self.title = self.to_unicode_or_bust(''.join(self.imdb_object['title']))
        if 'genres' in keys:
            self.genres = self.to_unicode_or_bust(' '.join(self.imdb_object['genres']).decode('utf-8'))
        if 'runtimes' in keys:
            self.runtime = self.to_unicode_or_bust(' '.join(self.imdb_object['runtime']).decode('utf-8'))
        if 'languages' in keys:
            self.language = self.to_unicode_or_bust(' '.join(self.imdb_object['language']).decode('utf-8'))
        if 'rating' in keys:
            self.rating = self.imdb_object['rating']
        if 'plot' in keys:
            self.plot = self.to_unicode_or_bust(' '.join(self.imdb_object['plot']).decode('utf-8'))
            self.plot = self.plot[:self.plot.find('::')]
