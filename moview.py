#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
from imdbcom import ImdbCom
from jinja2 import Environment, FileSystemLoader
import mimetypes
from movie import Movie
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


def is_directory_or_file(path):
    """
    Parser check method.
    Check if specified path points to valid directory or file.
    """
    print path
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


def main():
    args = process_arguments()
    movies_list = []

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

    #Obtain movie details from imdb.
    unique_movies_dict = {}
    for movie in movies_database:
        if movie.imdb_id != NO_IMDBID_FOUND:
            movie.imdb_object = \
                ImdbCom.get_movie_data_from_imdbcom(movie.imdb_id)
            movie.prepare_data_from_imdb()
            if movie.imdb_id not in unique_movies_dict.keys():
                print "\"%s\" processed." % movie.title
            unique_movies_dict[movie.imdb_id] = movie 
        else:
            print "\"%s\" not processed - no imdb id detected." % movie.path
                
    #Preapre list of not duplicated movies
    #Each movie objact on this list contains data from imdb.com
    unique_movies_list = unique_movies_dict.values()

    #Finally render index.html file
    
    os.chdir(sys.path[0])
    #Prepare environment for jinja2
    env = Environment(loader = FileSystemLoader('templates'))
    #Select template
    template = env.get_template('index.html')
    #Render results to index.html file
    rendered_file = open('index.html','w')
    rendered_file.write(template.render(movielist=unique_movies_list))
    rendered_file.close()
    #That's it!

    print "index.html with movie list has been " + \
        "generated in the current directory."
    print "Thanks for using MoView!"

    return sys.exit(0)

if __name__ == "__main__":
    main()

