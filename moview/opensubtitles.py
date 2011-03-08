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
            cls.country_code = getattr(settings, "OPENSUBTITLES_COUNTRY_CODE")
            cls.ua = getattr(settings, "OPENSUBTITLES_USER_AGENT")
            cls.url = getattr(settings, "OPENSUBTITLES_XMLRPC_SERVER")
            cls.okCode = getattr(settings, "OPENSUBTITLES_SUCCESS_CODE")
        else:
            print "Lack of opensubtitles.org server configuration data." + \
                "Please check settings."
            sys.exit(2)

        cls.proxy = xmlrpclib.ServerProxy(cls.url)
        cls.login = cls.proxy.LogIn(cls.user, cls.password, \
                                        cls.country_code, cls.ua)

        if cls.okCode not in cls.login['status']:
            print "Can't log to opensubtitles.org server. Cause: %s" \
                % cls.login['status']
            sys.exit(2)
        else:
            cls.token = cls.login['token']

    @classmethod
    def get_movie_data(cls, movies_to_check):
        """
        Obtains IMDB ID for movies specified in movies_to_check list.
        Each movies in the list is pointed by valid path.
        """
        if not cls.token:
            cls._setup_connection()
        movies_hash_list = []
        movies_hash_to_path_dict = {}
        """Final movie dictionary which maps movie path to IMDBID"""
        movies_final_dict = {}
        """
        Prepare:
        - list of movies hashes which will be sent to opensubtitles.org server
        - dictionary which stores link between movie hash and its path
        - partly filled final results dictionary in case when hash has not
        been calculated properly
        """
        for movie_path in movies_to_check:
            """Check if movie file is still under the specified path"""
            if os.path.isfile(movie_path):
                movie_hash = cls._calculate_hash(movie_path)
                if movie_hash != HASH_NOT_CALCULATED:
                    movies_hash_list.append(movie_hash)
                    movies_hash_to_path_dict[movie_hash] = movie_path
                else:
                    movies_final_dict[movie_path] = NO_IMDBID_FOUND

        """
        Connects with opensubtitles.org to obtain movie related data
        Important note:
        open subtitles returns all hashes which were transferred in the request
        even if movie has not been found. In other words:
        - if movie data has been deteced then 'data' list is returned
        - if movie data has not been deteced then 'data' list is empty
        """
        movies_results = cls.proxy.CheckMovieHash(cls.token, movies_hash_list)

        for hash_value in movies_results['data']:
            """Check if movie has been found"""
            if len(movies_results['data'][hash_value]) != 0:
                """Store movie IMDB in final results dictionary"""
                movies_final_dict[movies_hash_to_path_dict[hash_value]] = \
                    movies_results['data'][hash_value]["MovieImdbID"]
            else:
                "Mark IMDB ID as not found for not recognized movie"
                movies_final_dict[movies_hash_to_path_dict[hash_value]] = \
                    NO_IMDBID_FOUND

        """Close the connection and logout from the server"""
        cls.proxy.LogOut(cls.token)
        cls.token = None

        return movies_final_dict

    @classmethod
    def _calculate_hash(cls, path):
        """
        Method used to calculate unique movie hash.
        Obtained from API resources for opensubtitbles.org
        """
        try:

            longlongformat = 'q'  # long long
            bytesize = struct.calcsize(longlongformat)

            movie_file = open(path, "rb")

            filesize = os.path.getsize(path)
            hash_value = filesize

            if filesize < 65536 * 2:
                return "SizeError"

            for tmp_x in range(65536 / bytesize):
                tmp_buffer = movie_file.read(bytesize)
                (l_value,)= struct.unpack(longlongformat, tmp_buffer)
                hash_value += l_value
                hash_value = hash_value & 0xFFFFFFFFFFFFFFFF #to remain as 64bit number

            movie_file.seek(max(0, filesize - 65536), 0)
            for tmp_x in range(65536 / bytesize):
                tmp_buffer = movie_file.read(bytesize)
                (l_value,)= struct.unpack(longlongformat, tmp_buffer)
                hash_value += l_value
                hash_value = hash_value & 0xFFFFFFFFFFFFFFFF

            movie_file.close()
            returnedhash_value = "%016x" % hash_value
            #store calculated hash_value
            return returnedhash_value

        except(IOError):
            return HASH_NOT_CALCULATED
