import argparse
from imdbcom import ImdbCom
import mimetypes
from movie import Movie
from movielistview import MovieListView
from opensubtitles import OpenSubtitles
import os
import sys

NO_IMDBID_FOUND = -1

def get_list_of_files(path, option = None):
    """
    Generates list of absolute paths to video files eg. /home/user/Movies/Matrix.avi
    Options:
    - single - scan single file
    - folder - scan specified folder (non-recursivly)
    - recursive - scan recursivly specified folder
    """
    listOfMovies = []
    if option == 'single':
        if is_movie(path):
            listOfMovies.append(path)
    elif option == 'folder':
        for item in os.listdir(path):
            singleFilePath = os.path.join(path, item)
            if is_movie(singleFilePath):
                listOfMovies.append(singleFilePath)                
    elif option == 'recursive':
        for root, dirname, filenames in os.walk(path):
            filelist = [ os.path.join(root,fi) for fi in filenames ]
            for singleFilePath in filelist:
                if is_movie(singleFilePath):
                    listOfMovies.append(singleFilePath)
    return listOfMovies

def is_directory(path):
    """
    Parser check method.
    Check if specified path points to valid directory.
    """
    if os.path.isdir(path):
        return path
    else:
        msg = "%s is not a directory" % path
        raise argparse.ArgumentTypeError(msg)

def is_file(path):
    """
    Parser check method.
    Checks if specified path points to valid file.
    """
    if os.path.isfile(path):
        return path
    else:
        msg = "%s is not a file" % path
        raise argparse.ArgumentTypeError(msg)
                        
def is_movie(path):
    """
    Checks if absolute path points to file and if selected file is video file.
    """
    if os.path.isfile(path):
        fileType = mimetypes.guess_type(path)        
        if fileType[0] != None and 'video' in fileType[0]:
            return True        
    return False
    
def main(argv):
    
    programDescription = 'Script obtains movie data from common Internet '
    programDescription += 'sources like imdb.com, filmweb.pl etc. '
    programDescription += 'Movie title is detected by file name or/and hash value. '

    programUsage = 'python %(prog)s [options] path or filename'

    parser = argparse.ArgumentParser(description = programDescription, usage = programUsage)
    parser.add_argument('-f', '--folder', metavar='PATH', type=is_directory, \
                            help = 'Obtains data for movie file(s) stored in the specified folder')
    parser.add_argument('-s', '--single', metavar='FILE', type=is_file, \
                            help = 'Obtains data for a single movie file')
    parser.add_argument('-r', '--recursive', metavar='PATH', type=is_directory, \
                            help = 'Obtains data for movie files from ' + \
                            'a folder which is scanned recursively')

    args = parser.parse_args()
    
    moviesList = []

    if (args.single):        
        moviesList = get_list_of_files(args.single, 'single')
    elif (args.folder):        
        moviesList = get_list_of_files(args.folder, 'folder')
    elif (args.recursive):        
        moviesList = get_list_of_files(args.recursive, 'recursive')

    movieDict = {}
    movieDict = OpenSubtitles.get_movie_data(moviesList)
    del moviesList

    moviesDatabase = []
    for element in movieDict.items():
        movieObj = Movie()
        movieObj.IMDBID = element[1]
        movieObj.path = element[0]
        moviesDatabase.append(movieObj)
    del movieDict

    for movie in moviesDatabase:
        if movie.IMDBID != NO_IMDBID_FOUND:
            movie.imdbObject = \
                ImdbCom.get_movie_data_from_imdbcom(movie.IMDBID)
            movie.prepare_data_from_imdb()
    

    f = open('index.html', 'w')
    f.write(MovieListView(moviesDatabase).render())
    f.close()

    return sys.exit(0)

if __name__ == "__main__":
    main(sys.argv[1:])
