from optparse import OptionParser
import sys
import xmlrpclib
import logging
import struct
import os
import glob 

OK = 0
NOK = -1

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
        self.movieTitle = ""
        self.hash = 0

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


def single_file(filename):
    #intiate connection to opensubtitles.org
    servInstance = Server()

    #below test code - please ignore for now
    #intitiate Movie object
    movie = Movie()
    moviesToCheck = []
    moviesResults = []
    if (movie.hash_file(filename) == OK):
        moviesToCheck.append(movie.hash)
        moviesResults, result = servInstance.get_movie_data(moviesToCheck)
        if result == OK:
            for element in moviesToCheck:
                print moviesResults['data'][element]

def directory_scan(path):

    #intiate connection to opensubtitles.org
    servInstance = Server()

    os.chdir(path)
    fileList = glob.glob("*.avi" or "*.mpg")
    if len(fileList) == 0:
        return sys.exit(2)

    movieList = []
    for element in fileList:
        movie = Movie()
        if (movie.hash_file(element) == OK):
            movieList.append(movie)

    moviesToCheck = []
    for movie in movieList:
        moviesToCheck.append(movie.hash)

    moviesResults, result = servInstance.get_movie_data(moviesToCheck)
    if result == OK:
        for element in moviesToCheck:
            print moviesResults['data'][element]

def directory_scan_recursive(path):

    #intiate connection to opensubtitles.org
    servInstance = Server()
    os.chdir(path)
    finalList = []
    for root, dirname, filenames in os.walk(path):

        os.chdir(root)

        fileList = glob.glob("*.avi")
        for element in fileList:
            finalList.append(os.getcwd() + "/" + element)

    print finalList

    if len(finalList) == 0:
        return sys.exit(2)

    movieList = []
    for element in finalList:
        movie = Movie()
        if (movie.hash_file(element) == OK):
            movieList.append(movie)

    moviesToCheck = []
    for movie in movieList:
        moviesToCheck.append(movie.hash)

    moviesResults, result = servInstance.get_movie_data(moviesToCheck)
    if result == OK:
        for element in moviesToCheck:
            print moviesResults['data'][element]

        
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

    if options.filename:
        single_file(options.filename)
    elif options.folder:
        directory_scan(options.folder)
    elif options.folders:
        directory_scan_recursive(options.folders)
    


    

if __name__ == "__main__":
    main(sys.argv[1:])
