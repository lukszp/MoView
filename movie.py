NO_IMDBID_FOUND = -1


class Movie(object):
    """
    Store data about movie object.
    Data is obtained from:
    imdb.com
    """

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

        keys = self.imdbObject.keys()
        if ('title' in keys):
            self.title = ''.join(self.imdbObject['title'])
        if ('genres' in keys):
            self.genres = ' '.join(self.imdbObject['genres'])
        if ('runtimes' in keys):
            self.runtime = ' '.join(self.imdbObject['runtime'])
        if ('languages' in keys):
            self.language = ' '.join(self.imdbObject['language'])
        if ('rating' in keys):
            self.rating = self.imdbObject['rating']
        if ('plot' in keys):
            self.plot = ' '.join(self.imdbObject['plot'])
            self.plot = self.plot[:self.plot.find('::')]
