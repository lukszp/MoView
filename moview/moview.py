#!/usr/bin/env python
import argparse
from imdbcom import ImdbCom
from jinja2 import Environment, FileSystemLoader
import mimetypes
from movie import Movie
from opensubtitles import OpenSubtitles
import os
import re
import shutil
import sys


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


def is_directory_or_file(path):
    """
    Parser check method.
    Check if specified path points to valid directory or file.
    """
    if os.path.isdir(path):
        return 'folder', path
    elif os.path.isfile(path):
        return 'single', path
    else:
        msg = "%s is not a directory or file" % path
        raise argparse.ArgumentTypeError(msg)


def is_movie(path):
    """
    Checks if absolute path points to file and if selected file is video file.
    """
    if os.path.isfile(path):
        file_type = mimetypes.guess_type(path)
        if file_type[0] != None and 'video' in file_type[0]:
            return True
    return False

def obtain_title_and_year(movie):
    #Obtains title and year from file name or dir name
    pattern = '^(.+)(\d{4})'
    file_name = os.path.basename(movie.path)
    search_result = re.search(pattern, file_name)
    #Obtain from file name
    if search_result:
        movie.title = strip_non_alphanumeric(search_result.groups()[0])
        movie.year = strip_non_alphanumeric(search_result.groups()[1])
    #if not possible then check upper directory
    else:
        up_dir_name = os.path.split(os.path.dirname(movie.path))[1]
        search_result = re.search(pattern, up_dir_name)
        if search_result:
            movie.title = strip_non_alphanumeric(search_result_2.groups()[0])
            movie.year = strip_non_alphanumeric(search_result_2.groups()[1])

def process_arguments():

    description = 'MoView obtains movie related data from the common internet'
    description += ' resources like imdb.com or filmweb.pl and renders results'
    description += ' to index.html file.'

    program_usage = './%(prog)s [-h] [-r] path or filename'

    parser = argparse.ArgumentParser(description = description,
                                     usage = program_usage)
    #Optional argument definition
    parser.add_argument('-r', '--recursive', 
                        action='store_true',
                        help='obtain data for movie file(s) from ' + \
                            'a folder which is scanned recursively')
    #Positional argument definition
    parser.add_argument('path', 
                        metavar='directory/file', 
                        type=is_directory_or_file,
                        help='obtain movie data for the specified' + \
                            ' file or directory')
    args = parser.parse_args()
    return args

def strip_non_alphanumeric(input_string):
    pattern = re.compile('[\W_]+')
    return pattern.sub(' ', input_string) 

def main():
    args = process_arguments()
    movies_list = []
    os.path.dirname( os.path.realpath( __file__ ) )

    #Single file should be checked
    if args.path[0] == 'single':
        movies_list = get_list_of_files(args.path[1], 'single')
    #Folder should be scanned recusrivly
    elif args.path[0] == 'folder' and args.recursive:
        movies_list = get_list_of_files(args.path[1], 'recursive')
    #Folder 
    else:
        movies_list = get_list_of_files(args.path[1], 'folder')

    print "Working..."

    #Obtain imdb id for each movie file
    movie_dict = {}
    movie_dict = OpenSubtitles.get_movie_data(movies_list)
    del movies_list

    #Create movies database which contains movie objects
    movies_database = []
    for element in movie_dict.items():
        movie_obj = Movie()
        movie_obj.imdb_id = element[1]
        movie_obj.path = element[0]
        movies_database.append(movie_obj)
    del movie_dict

    #For movies which has not imdb id detected try to obtain title
    #from the file name
    #File name must be in such format: mobie_title_year(4 digits)_extension

    for movie in movies_database:
        if movie.imdb_id == None:
            obtain_title_and_year(movie)
            print "obtained! %s" % (movie.title)

    #Obtain movie details from imdb.
    unique_movies_dict = {}
    for movie in movies_database:
        #imdb id detected - take movie data from imdb.com
        if movie.imdb_id != None:
            movie.imdb_object = \
                ImdbCom.get_movie_data_from_imdbcom(movie.imdb_id)
            movie.prepare_data_from_imdb()
            if movie.imdb_id not in unique_movies_dict.keys():
                print "\"%s\" processed." % movie.title
            unique_movies_dict[movie.imdb_id] = movie 
        #imdb id is not known but title has been obtained from file name
        elif movie.title != None:
            movie.imdb_object, movie.imdb_id = \
                ImdbCom.search_movie_by_title(movie)
            if movie.imdb_object:
                movie.prepare_data_from_imdb()
                if movie.imdb_id not in unique_movies_dict.keys():
                    print "\"%s\" processed." % movie.title
                unique_movies_dict[movie.imdb_id] = movie 
        else:
            print "\"%s\" not processed." % movie.path
                    
                
    #Preapre list of not duplicated movies
    #Each movie objact on this list contains data from imdb.com
    unique_movies_list = unique_movies_dict.values()

    #Finally render index.html file
    
    #Prepare environment for jinja2
    execution_path = os.path.dirname(os.path.realpath(__file__))
    templates_path = os.path.join(execution_path, 'templates')
    static_path = os.path.join(execution_path, 'static')
    #Prepare path for copying static files to cwd
    templates_cwd_path = os.path.join(os.getcwd(), 'moview/templates')
    static_cwd_path = os.path.join(os.getcwd(), 'moview/static')
    #Remove moview tmp files if already exists in cwd
    try:
        shutil.rmtree(os.path.join(os.getcwd(), 'moview'))
    except:
        pass
    #Copy static files to cwd under moview direcotry
    shutil.copytree(templates_path, templates_cwd_path)
    shutil.copytree(static_path, static_cwd_path)
    #Prepare environment for jinja2
    env = Environment(loader = FileSystemLoader(templates_path))
    #Select template
    template = env.get_template('index.html')
    #Render results to index.html file
    rendered_file = open('index.html','w')
    rendered_file.write(template.render(movielist=unique_movies_list).encode('utf-8'))
    rendered_file.close()
    #That's it!

    print "index.html with movie list has been " + \
        "generated in the current directory."
    print "Thanks for using MoView!"

    return sys.exit(0)

if __name__ == "__main__":
    main()

