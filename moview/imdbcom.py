import imdb


class ImdbCom():
    """
    ImdbCom class retries movie data from imdb.com database
    Data is retrivied based on imdb movie id.
    Input: imdb movie id.
    Output: imdb movie object.
    """
    imdb_access = None

    @classmethod
    def _setup_connection(cls):
        """Setups connection to imdb.com server"""
        try:
            cls.imdb_access = imdb.IMDb()
        except imdb.IMDbError, err:
            print "Problem with connectivity to imdb.com due to %s " \
               % (err)

    @classmethod
    def get_movie_data_from_imdbcom(cls, imdbid):
        """
        Retrivies movie object from imdb.com
        For more information about movie object please see:
        http://imdbpy.sourceforge.net/docs/README.package.txt
        """
        if cls.imdb_access == None:
            cls._setup_connection()

        movie = cls.imdb_access.get_movie(imdbid)
        return movie
