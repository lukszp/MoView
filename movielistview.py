import pystache


class MovieListView(pystache.View):
    """
    Renders list of movies.
    Input: list of movies.
    Output: rendered html page.
    """
    template_path = 'templates'

    def __init__(self, movies_database=[]):
        pystache.View.__init__(self)
        self.movies_database = movies_database

    def empty(self):
        return len(self.movie()) == 0

    def movie(self):
        movies = []
        for movie in self.movies_database:
            if movie.title != None:
                movies.append({'pathValue': movie.path, 
                               'path': True,
                               'titleValue': movie.title, 
                               'title': True,
                               'genresValue': movie.genres, 
                               'genres': True,
                               'runtimeValue': movie.runtime, 
                               'runtime': True,
                               'languageValue': movie.language, 
                               'language': True,
                               'ratingValue': movie.rating, 
                               'rating': True,
                               'plotValue': movie.plot, 
                               'plot': True})

        movies_alph_sorted_list = sorted(movies, key=lambda k: k['titleValue'])

        return movies_alph_sorted_list

    def movie_content(self):
        return not self.empty()
