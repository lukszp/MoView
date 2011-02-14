from optparse import OptionParser
import sys
import xmlrpclib
import logging
import struct
import os
import glob 
import imdb

#ERROR CODES
OK = 0
NOK = -1
NO_MOVIES_DETECTED = "No movie files have been found in the specified path."

#PURPOSE:       connects to opensubtitles.org to obtain
#               IMDB movie id and full title based on hash
#PRECONDITIONS: internet connection must be available
#               movie path must be valid
#RETURN:        if movie path is OK and movie is found in
#               opensubtitles.org database then IMDB ID
#               movie title are returned


class Server(object):

    def __init__(self):
        self.user = ""
        self.password = ""
        self.country_code = "PL"
        self.ua = "OS Test User Agent"
        self.API_address = "http://api.opensubtitles.org/xml-rpc"
        self.token = 0
        self.OK_code = "200 OK"

    def init_connection(self):
        self.server = xmlrpclib.ServerProxy(self.API_address)
        logging.debug("Connected")
        self.login = self.server.LogIn(self.user, self.password,
                                       self.country_code, self.ua)
        if self.OK_code in self.login['status']:
            self.token = self.login['token']
            logging.debug("Logged in")
            return OK
        else:
            logging.debug("Not logged in - abort")
            return NOK

    def get_movie_data(self, moviesToCheck):
        self.init_connection()
        moviesData = []
        if self.token == 0:
            logging.debug("Lack of valid token")
            return moviesData, NOK
        moviesData = self.server.CheckMovieHash(self.token, moviesToCheck)
        self.logout()
        return moviesData, OK

    def logout(self):
        if self.token == 0:
            logging.debug("Lack of valid token")
            return NOK
        result = self.server.LogOut(self.token)
        if self.OK_code in result['status']:
            logging.debug("Logout successful")
            return OK
        else:
            logging.debug("Logout unsuccesful")
            return NOK

#PURPOSE:       stores data about movie
#PRECONDITIONS: valid path to movie file

class Movie(object):

    def __init__(self):
        self.IMDBID = 0
        self.movieTitle = "Not found"
        self.hash = 0
        self.moviePath = ""
        self.imdb_movie_object = 0

    def __str__(self):
        return "IMDBID: %s \t Title: %s \t Path: %s" \
            % (self.IMDBID, self.movieTitle, self.moviePath)

    def get_imdb_data(self, imdb_access):
        if self.IMDBID != 0:
            self.imdb_movie_object = \
                imdb_access.get_movie(self.IMDBID)

    def hash_file(self, path):
    #method imported directly from opensubtitles.org
    #needed to calculate hash
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
            logging.debug("Hash calculated")
            self.hash = returnedhash
            return OK

        except(IOError):
            logging.debug("Hash not calculated")
            return NOK

def create_movies_dict(finalList):
    movieDict = {}
    movieDict = calculate_movies_hash(finalList, movieDict)
    movieDict = get_movies_data(movieDict)
    return movieDict

def calculate_movies_hash(moviesList, movieDict):

    for element in moviesList:
        movie = Movie()
        if (movie.hash_file(element) == OK):
            if (movie.hash not in movieDict):
                movie.moviePath = element
                movieDict[movie.hash] = movie
    return movieDict

def get_movies_data(movieDict):

    servInstance = Server()

    moviesToCheck = []
    for key in movieDict:
        moviesToCheck.append(movieDict.get(key).hash)

    moviesResults, result = servInstance.get_movie_data(moviesToCheck)

    if result == OK:
        for element in moviesToCheck:
            if len(moviesResults['data'][element]) != 0:
                movieDict[moviesResults['data'][element]["MovieHash"]].movieTitle \
                    = moviesResults['data'][element]["MovieName"]
                movieDict[moviesResults['data'][element]["MovieHash"]].IMDBID \
                    = moviesResults['data'][element]["MovieImdbID"]

    return movieDict

def single_file(filename):

    finalList = []
    finalList.append(filename)
    return create_movies_dict(finalList)

def directory_scan(path):

    os.chdir(path)
    finalList = []
    fileList = glob.glob("*.avi" or "*.mpg")
    for element in fileList:
        #use absolut path to the movie file
        finalList.append(os.getcwd() + "/" + element)

    if len(finalList) == 0:
        print NO_MOVIES_DETECTED
        return sys.exit(2)
        
    return create_movies_dict(finalList)

def directory_scan_recursive(path):
    
    #change path to selected one
    os.chdir(path)
    finalList = []

    #scan all folders under the path for movies
    for root, dirname, filenames in os.walk(path):
        os.chdir(root)
        fileList = glob.glob("*.avi" or "*.mpg")
        for element in fileList:
            #use absolut path to the movie file
            finalList.append(os.getcwd() + "/" + element)

    #no movies found then exit
    if len(finalList) == 0:
        print NO_MOVIES_DETECTED
        return sys.exit(2)

    return create_movies_dict(finalList)        

def print_movie_dict(movieDict):
    for movie in movieDict.values():
        print movie
        print "-----------------------"
        print movie.imdb_movie_object.summary()

def get_imdb_movies_data(movieDict, imdb_access):
    for movie in movieDict.values():
        movie.get_imdb_data(imdb_access)

def main(argv):
    parser = OptionParser()
    parser.add_option("-s", "--single", dest="filename",
                  help="obtains date for a single file", metavar="FILE")
    parser.add_option("-f", "--folder", dest="folder",
                      help="obtains data for files in a folder")
    parser.add_option("-F", "--folder-recursive", dest="folders",
                      help="obtains data for files in a folders scanning them recursively")
    parser.add_option("-d", "--debug", dest="debug", default=False, action="store_true",
                      help="enables debug mode")
    (options, args) = parser.parse_args()

    if options.debug == True:
    #debug
        logging.basicConfig(level=logging.DEBUG)

    movieDict = {}

    if options.filename:
        movieDict = single_file(options.filename)
    elif options.folder:
        movieDict = directory_scan(options.folder)
    elif options.folders:
        movieDict = directory_scan_recursive(options.folders)
    
    imdb_access = imdb.IMDb()    
    get_imdb_movies_data(movieDict, imdb_access)
    print_movie_dict(movieDict)
    

if __name__ == "__main__":
    main(sys.argv[1:])
