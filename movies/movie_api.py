# ################################
#   Copyright (c) 2021 Jim Bray
#       All Rights Reserved
# ################################
import requests
from config_control import ConfigJson

config = ConfigJson()
API_SEARCH_END_POINT = "https://api.themoviedb.org/3/search/movie"
API_END_POINT = "https://api.themoviedb.org/3/movie/"


class MovieList:
    """
    helper for the movie database api
    """
    def __init__(self):
        self.search = ""
        self.api_ep_search = API_SEARCH_END_POINT
        self.api_ep_id = API_END_POINT
        self.parameters = {}
        self.data = {}
        self.search_data = {}
        self.original_title = ""
        self.overview = ""
        self.poster_path = ""
        self.image = ""
        self.release_date = ""
        self.vote_average: float = 0.0

    def poll_api_search(self, movie_title):
        """
        polls the api with a search query
        :param movie_title: the movie titie to search for
        :return: json data
        """
        self.parameters = {
            "api_key": config.read(item_to_read="MOVIE_API_KEY"),
            "query": movie_title
        }
        response = requests.get(self.api_ep_search, params=self.parameters)
        response.raise_for_status()
        self.search_data = response.json()

    def choice_from_list(self):
        """
        queries for the selected movie title from the initial search result
        :return: list of titles and release dates
        """
        a_list = []
        for count, value in enumerate(self.search_data["results"]):
            if value.get('release_date'):
                date = value.get('release_date')[:4]
            else:
                date = value.get('release_date')
            title = value.get('original_title')
            id = value.get('id')
            movies = (id, title, date)
            a_list.append(movies)
        return a_list

    def poll_api_id(self, movie_id):
        """
        polls the api for the specific movie id
        :param movie_id: movie id user selected from the choice_from_list functon
        :return: json data
        """
        self.parameters = {
            "api_key": config.read(item_to_read="MOVIE_API_KEY")
        }
        self.api_ep_id = self.api_ep_id + str(movie_id)
        # print(self.api_ep_id)
        response = requests.get(self.api_ep_id, params=self.parameters)
        response.raise_for_status()
        self.data = response.json()

    def get_results(self):
        """
        colects the data from the poll_api_id function
        :return: each attribute from the class object instance
        """
        self.original_title = self.data["original_title"]
        self.overview = self.data["overview"]
        self.release_date = self.data["release_date"][:4]
        self.vote_average = self.data["vote_average"]
        self.poster_path = self.data["poster_path"]
        self.get_img_file()

    def get_img_file(self):
        """
        converts the specified poster into a url path
        :return: url to the specified image file
        """
        image_url = "https://image.tmdb.org/t/p/w500/"
        try:
            self.image = image_url + self.poster_path
        except TypeError:
            self.image = "https://www.themoviedb.org/assets/2/v4/glyphicons/basic/glyphicons-basic-38-picture-grey-c2ebdbb057f2a7614185931650f8cee23fa137b93812ccb132b9df511df1cfac.svg"

        return self.image


if __name__ == "__main__":
    wrs = MovieList()

    # SEARCH FUNCTIONS CHECK
    # wrs.poll_api_search("Fight Club")
    # print(wrs.choice_from_list())
    # for item in wrs.choice_from_list():
    #     print(f"{item[0]} {item[1]} {item[2]} ")

    # FIND BY ID FUNCTIONS CHECK
    wrs.poll_api_id(259016)
    wrs.get_results()
    print(wrs.original_title)
    print(wrs.overview)
    print(wrs.release_date)
    print(wrs.vote_average)
    print(wrs.image)
