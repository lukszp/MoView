import argparse
from imdbcom import ImdbCom
import mimetypes
from movie import Movie
from movielistview import MovieListView
from opensubtitles import OpenSubtitles
import os
import sys

NO_IMDBID_FOUND = -1


def get_list_of_files(path, option=None):
    """
    Generates list of absolute paths to video
    files eg. /home/user/Movies/Matrix.avi
    Options:
    - single - scan single file
    - folder - scan specified folder (non-recursivly)
    - recursive - scan recursivly specified folder
    """
    list_of_movies = []
    if option == 'single':
        if is_movie(path):
            list_of_movies.append(path)
    elif option == 'folder':
        for item in os.listdir(path):
            single_file_path = os.path.join(path, item)
            if is_movie(single_file_path):
                list_of_movies.append(single_file_path)
    elif option == 'recursive':
        for root, dirname, filenames in os.walk(path):
            filelist = [os.path.join(root, fi) for fi in filenames]
            for single_file_path in filelist:
                if is_movie(single_file_path):
                    list_of_movies.append(single_file_path)
    return list_of_movies


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


def is_directory_tf(path):
    """
    Check if specified path points to valid directory.
    """
    if os.path.isdir(path):
        return True
    else:
        return False

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


def is_file_tf(path):
    """
    Checks if specified path points to valid file.
    """
    if os.path.isfile(path):
        return True
    else:
        return False


def is_movie(path):
    """
    Checks if absolute path points to file and if selected file is video file.
    """
    if os.path.isfile(path):
        file_type = mimetypes.guess_type(path)
        if file_type[0] != None and 'video' in file_type[0]:
            return True
    return False


def main(argv):

    movies_list = []
    """
    Check for default option which is:
    - if user points to a directory act as with -f option
    - if user points to a movie file act as with -s option
    """
    if len(argv) == 1:
        if is_directory_tf(argv[0]):
            movies_list = get_list_of_files(argv[0], 'folder')
        elif is_file_tf(argv[0]):
            movies_list = get_list_of_files(argv[0], 'single')
        else:
            print "%s is not a directory nor movie file. " % (argv[0])
            print "Please use python movies.py --help for help"
            sys.exit(2)
    else:
        """
        Parse options.
        -s - extract data for a single file
        -f - extract data for a single directory
        -r - extract data for a directory and for sub-directories
        using recurisve mode
        """
        program_description = 'Script obtains movie data from common Internet '
        program_description += 'sources like imdb.com, filmweb.pl etc. '
        program_description += 'Movie title is detected by file name or/and hash value. '

        program_usage = 'python %(prog)s [options] path or filename'

        parser = argparse.ArgumentParser(description=program_description, usage=program_usage)
        parser.add_argument('-f', '--folder', metavar='PATH', type=is_directory, \
                                help='Obtains data for movie file(s) stored in the specified folder')
        parser.add_argument('-s', '--single', metavar='FILE', type=is_file, \
                                help='Obtains data for a single movie file')
        parser.add_argument('-r', '--recursive', metavar='PATH', type=is_directory, \
                                help='Obtains data for movie files from ' + \
                                'a folder which is scanned recursively')

        args = parser.parse_args()


        if (args.single):
            movies_list = get_list_of_files(args.single, 'single')
        elif (args.folder):
            movies_list = get_list_of_files(args.folder, 'folder')
        elif (args.recursive):
            movies_list = get_list_of_files(args.recursive, 'recursive')

    print "Working..."

    movie_dict = {}
    movie_dict = OpenSubtitles.get_movie_data(movies_list)
    del movies_list

    movies_database = []
    for element in movie_dict.items():
        movie_obj = Movie()
        movie_obj.imdb_id = element[1]
        movie_obj.path = element[0]
        movies_database.append(movie_obj)
    del movie_dict

    unique_movies_dict = {}

    for movie in movies_database:
        if movie.imdb_id != NO_IMDBID_FOUND:
            movie.imdb_object = \
                ImdbCom.get_movie_data_from_imdbcom(movie.imdb_id)
            movie.prepare_data_from_imdb()
            unique_movies_dict[movie.imdb_id] = movie 
        
    unique_movies_list = unique_movies_dict.values()

    rendered_view_file = open('index.html', 'w')
    rendered_view_file.write(MovieListView(unique_movies_list).render())
    rendered_view_file.close()

    print "index.html with movie list has been generated in the current directory."
    print "Thanks for using MoView!"

    return sys.exit(0)

if __name__ == "__main__":
    main(sys.argv[1:])
