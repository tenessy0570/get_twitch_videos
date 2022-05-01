from requests_html import HTMLSession, HTML
from . import exceptions


class RequestMaker:
    """
    A class to send request and get html response
    """

    def __init__(self):
        self._html = None
        self.twitch_base_url = 'https://www.twitch.tv'
        self._allowed_video_types = ('clips', 'archives', 'highlights', 'moments', 'uploads', 'collections', 'all')

    def make_request(self, username, video_type) -> None:
        """Makes request to twitch user's videos list and saves response's html

        :param username: twitch username.
        :param video_type: type of video, like 'clips' or 'highlights'.
        """

        if video_type not in self._allowed_video_types:
            raise exceptions.WrongVideoTypeException

        self._make_request(username, video_type)

    def _make_request(self, username, video_type):
        videos_url_base_url = self.twitch_base_url + f'/{username}/videos?filter='
        video_type_url = videos_url_base_url + video_type

        sleep_time = 1

        if video_type == 'clips':
            video_type_url += '&range=all'

        session = HTMLSession()

        html = session.get(video_type_url).html
        html.render(sleep=sleep_time, scrolldown=15)

        self._html = html

    def get_rendered_html(self) -> HTML:
        """Returns rendered requests_html.HTML object

        :return: HTML object
        """
        return self._html


class VideoScraper:
    """
    A class to scrape video links from twitch channel.
    """

    def __init__(self):
        self._video_links = dict()
        self._request_maker = RequestMaker()

    def scrape_videos(
            self, username: str, videos_type: str) -> dict:
        """Scrapes videos from twitch.tv user channel depending on type of videos you want to get.

        :param username: twitch username which videos you want to scrape.
        :param videos_type: type of video, like 'clips' or 'highlights'.
        :return: a dictionary with key=title of link, value=link url.
        """
        return self._scrape_videos(username, videos_type)

    def _scrape_videos(self, username: str, videos_type: str) -> dict:
        self._request_maker.make_request(username, videos_type)
        html = self._request_maker.get_rendered_html()

        links_dict = self._get_dict_of_links(html)
        return links_dict

    def _get_dict_of_links(self, html: HTML) -> dict:
        links = html.find('a[lines="1"]')
        links_dict = {
            link.find('h3', first=True).text if link.find('h3', first=True).text != '' else 'no title':
                self._request_maker.twitch_base_url + link.attrs['href']
            for link in links
        }
        return links_dict


# class FileWriter:
#     """
#     A class to deal with files.
#     """
#
#     def __init__(self, file: str, open_type: str):
#         self._file = file,
#         self._open_type = open_type
#
#     def write_to_file(self, data: str) -> None:
#         """Writes data to object instance's file.
#
#         :param data: a text to save in file.
#         """
#         with open(self._file, self._open_type) as file:
#             file.write(data)
