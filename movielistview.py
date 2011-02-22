import pystache


class MovieListView(pystache.View):
    template_path = 'templates'
    
    def __init__(self, moviesDatabase = []):
        pystache.View.__init__(self)
        self.moviesDatabase = moviesDatabase

    def empty(self):
        return len(self.movie()) == 0

    def movie(self):
        movies = []
        for movie in self.moviesDatabase:
            if movie.title != None:
                movies.append({ 'pathValue' : movie.path, 'path' : True, 
                                'titleValue' : movie.title, 'title' : True,
                                'genresValue' : movie.genres, 'genres' : True,
                                'runtimeValue' : movie.runtime, 'runtime' : True,
                                'languageValue' : movie.language, 'language' : True,
                                'ratingValue' : movie.rating, 'rating' : True,
                                'plotValue' : movie.plot, 'plot' : True })
        
        moviesAlphSortedList = sorted(movies, key=lambda k: k['titleValue'])

        return moviesAlphSortedList

    def movie_content(self):
        return not self.empty()


