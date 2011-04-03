import imdb
import re


class ImdbCom(object):
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

    @classmethod
    def search_movie_by_title(cls, movie):
        #Retrives movie object and imdb id from imdb.com
        #based on movie title
        #For more information about movie object please see:
        #http://imdbpy.sourceforge.net/docs/README.package.txt
        if cls.imdb_access == None:
            cls._setup_connection()

        search_results = cls.imdb_access.search_movie(movie.title)
        #imdb.com return list of items which contains
        #imdb local movie id and long movie title (title + year)
        #List could containy many movies with same title
        for item in search_results:
            #obtain year from movie title
            result = re.search('(\d{4})', item['long imdb canonical title'])
            if result:
                #check if year obtained from file (movie.year) name is the same
                #as obtained from imdb.com
                if result.groups()[0] == movie.year:
                    #get imdb movie object for the selected item
                    cls.imdb_access.update(item)
                    #get imdb id for the selected item
                    imdb_id = cls.imdb_access.get_imdbID(item)
                    return item, imdb_id 
        #nothing has been found
        return None, None
