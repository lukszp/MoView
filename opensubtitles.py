import os
import settings
import struct
import sys
import xmlrpclib

"""
Error codes:
"""
HASH_NOT_CALCULATED = -1
NO_IMDBID_FOUND = -1


class OpenSubtitles():
    """
    Singleton class which allows to obtain movie IMDB ID based
    on hash value calculated for each movie specified by path.
    Input delivered as list of path to movie files.
    """
    token = None

    @classmethod
    def _setup_connection(cls):
        if hasattr(settings, "OPENSUBTITLES_USER") and \
                hasattr(settings, "OPENSUBTITLES_PASS") and \
                hasattr(settings, "OPENSUBTITLES_COUNTRY_CODE") and \
                hasattr(settings, "OPENSUBTITLES_USER_AGENT") and \
                hasattr(settings, "OPENSUBTITLES_XMLRPC_SERVER") and \
                hasattr(settings, "OPENSUBTITLES_SUCCESS_CODE"):
            cls.user = getattr(settings, "OPENSUBTITLES_USER")
            cls.password = getattr(settings, "OPENSUBTITLES_PASS")
            cls.countryCode = getattr(settings, "OPENSUBTITLES_COUNTRY_CODE")
            cls.ua = getattr(settings, "OPENSUBTITLES_USER_AGENT")
            cls.url = getattr(settings, "OPENSUBTITLES_XMLRPC_SERVER")
            cls.okCode = getattr(settings, "OPENSUBTITLES_SUCCESS_CODE")
        else:
            print "Lack of opensubtitles.org server configuration data." + \
                "Please check settings."
            sys.exit(2)

        cls.proxy = xmlrpclib.ServerProxy(cls.url)
        cls.login = cls.proxy.LogIn(cls.user, cls.password, \
                                        cls.countryCode, cls.ua)

        if cls.okCode not in cls.login['status']:
            print "Can't log to opensubtitles.org server. Cause: %s" \
                % cls.login['status']
            sys.exit(2)
        else:
            cls.token = cls.login['token']

    @classmethod
    def get_movie_data(cls, moviesToCheck):
        """
        Obtains IMDB ID for movies specified in moviesToCheck list.
        Each movies in the list is pointed by valid path.
        """
        if not cls.token:
            cls._setup_connection()
        moviesHashList = []
        moviesHashToPathDict = {}
        """Final movie dictionary which maps movie path to IMDBID"""
        moviesFinalDict = {}
        """
        Prepare:
        - list of movies hashes which will be sent to opensubtitles.org server
        - dictionary which stores link between movie hash and its path
        - partly filled final results dictionary in case when hash has not
        been calculated properly
        """
        for moviePath in moviesToCheck:
            """Check if movie file is still under the specified path"""
            if os.path.isfile(moviePath):
                movieHash = cls._calculate_hash(moviePath)
                if movieHash != HASH_NOT_CALCULATED:
                    moviesHashList.append(movieHash)
                    moviesHashToPathDict[movieHash] = moviePath
                else:
                    moviesFinalDict[moviePath] = NO_IMDBID_FOUND

        """
        Connects with opensubtitles.org to obtain movie related data
        Important note:
        open subtitles returns all hashes which were transferred in the request
        even if movie has not been found. In other words:
        - if movie data has been deteced then 'data' list is returned
        - if movie data has not been deteced then 'data' list is empty
        """
        moviesResults = cls.proxy.CheckMovieHash(cls.token, moviesHashList)

        for hashValue in moviesResults['data']:
            """Check if movie has been found"""
            if len(moviesResults['data'][hashValue]) != 0:
                """Store movie IMDB in final results dictionary"""
                moviesFinalDict[moviesHashToPathDict[hashValue]] = \
                    moviesResults['data'][hashValue]["MovieImdbID"]
            else:
                "Mark IMDB ID as not found for not recognized movie"
                moviesFinalDict[moviesHashToPathDict[hashValue]] = \
                    NO_IMDBID_FOUND

        """Close the connection and logout from the server"""
        cls.proxy.LogOut(cls.token)
        cls.token = None

        return moviesFinalDict

    @classmethod
    def _calculate_hash(cls, path):
        """
        Method used to calculate unique movie hash.
        Obtained from API resources for opensubtitbles.org
        """
        try:

            longlongformat = 'q'  # long long
            bytesize = struct.calcsize(longlongformat)

            f = open(path, "rb")

            filesize = os.path.getsize(path)
            hash = filesize

            if filesize < 65536 * 2:
                return "SizeError"

            for x in range(65536 / bytesize):
                buffer = f.read(bytesize)
                (l_value,)= struct.unpack(longlongformat, buffer)
                hash += l_value
                hash = hash & 0xFFFFFFFFFFFFFFFF #to remain as 64bit number

            f.seek(max(0, filesize - 65536), 0)
            for x in range(65536 / bytesize):
                buffer = f.read(bytesize)
                (l_value,)= struct.unpack(longlongformat, buffer)
                hash += l_value
                hash = hash & 0xFFFFFFFFFFFFFFFF

            f.close()
            returnedhash = "%016x" % hash
            #store calculated hash
            return returnedhash

        except(IOError):
            return HASH_NOT_CALCULATED
