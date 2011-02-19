import imdb

class ImdbCom():
    imdb_access = None

    @classmethod
    def _setup_connection(cls):
        try:
            cls.imdb_access = imdb.IMDb()
        except imdb.IMDbError, err:
            print "Problem with connectivity to imdb.com due to %s " \
               % (err)
           

    @classmethod
    def get_movie_data_from_imdbcom(cls, imdbid):
        if cls.imdb_access == None:
            cls._setup_connection()

        movie = cls.imdb_access.get_movie(imdbid)
        return movie 
      
