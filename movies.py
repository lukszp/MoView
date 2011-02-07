import sys
import xmlrpclib
import logging
import struct
import os

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
        self.login = self.server.LogIn(self.user, self.password, self.country_code, self.ua)
        if self.OK_code in self.login['status']:
            self.token = self.login['token']
            logging.debug("Logged in")
            return OK
        else:
            logging.debug("Not logged in - abort")
            return NOK

    def get_movie_data(self, moviesToCheck):
        moviesData = []
        if self.token == 0:
            logging.debug("Lack of valid token")
            return moviesData, NOK
        moviesData = self.server.CheckMovieHash(self.token, moviesToCheck)
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
        
 
class Movie(object):

    def __init__(self):
        self.IMDBID = 0
        self.movieTitle = ""
    
    def hash_file(self,path): 
        try: 
        
            longlongformat = 'q'  # long long 
            bytesize = struct.calcsize(longlongformat) 
        
            f = open(path, "rb") 
        
            filesize = os.path.getsize(path) 
            hash = filesize 
        
            if filesize < 65536 * 2: 
                return "SizeError" 
                 
            for x in range(65536/bytesize): 
                buffer = f.read(bytesize) 
                (l_value,)= struct.unpack(longlongformat, buffer)  
                hash += l_value 
                hash = hash & 0xFFFFFFFFFFFFFFFF #to remain as 64bit number  
                         
    
            f.seek(max(0,filesize-65536),0) 
            for x in range(65536/bytesize): 
                buffer = f.read(bytesize) 
                (l_value,)= struct.unpack(longlongformat, buffer)  
                hash += l_value 
                hash = hash & 0xFFFFFFFFFFFFFFFF 
                 
            f.close() 
            returnedhash =  "%016x" % hash 
            #store calculated hash
            logging.debug("Hash calculated")
            self.hash = returnedhash
            return OK
    
        except(IOError): 
            logging.debug("Hash not calculated")
            return NOK


def main():
    #debug
    logging.basicConfig(level=logging.DEBUG)
    #intiate connection to opensubtitles.org
    servInstance = Server()
    servInstance.init_connection()

    #below test code - please ignore for now
    #intitiate Movie object
    movie = Movie()
    moviesToCheck = []
    moviesResults = []
    if (movie.hash_file("TG.avi") == OK):
        moviesToCheck.append(movie.hash)
        moviesToCheck.append("1234455")
        moviesToCheck.append(movie.hash)
        moviesResults, result = servInstance.get_movie_data(moviesToCheck)
        if result == OK:
            for element in moviesToCheck:
                print moviesResults['data'][element]

    #end of test code
    servInstance.logout()

if __name__ == "__main__":
    main()
