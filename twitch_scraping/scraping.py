import asyncio

import pyppeteer
from bs4 import BeautifulSoup
from pyppeteer.page import Page

from . import exceptions, utils
from .constants import allowed_video_types
from .typing import list_of_video_objects


class TwitchHtmlParser:
    """
    A class to parse html markup
    """

    def __init__(self):
        self._base_url = "https://www.twitch.tv"
        self._method_for = {"clips": self._parse_twitch_clips}
        self._parsed_videos: list_of_video_objects = list()

    def get_parsed_videos(self) -> list_of_video_objects:
        return self._parsed_videos

    def parse_twitch_html(self, html: str, videos_type: str) -> None:
        return self._method_for[videos_type](html)

    def _parse_twitch_clips(self, html: str) -> None:
        soup = BeautifulSoup(html, 'html.parser')

        videos_list = []

        container = soup.find_all('article', class_="Layout-sc-nxg1ff-0 frepDF")

        for article in container:
            video = dict()

            el_a = article.find_all('a')

            is_untitled = len(el_a) != 4
            element_a = el_a[1] if is_untitled else el_a[0]

            video_info_div = article.find_all('div', class_="ScWrapper-sc-uo2e2v-0 IbFZu tw-hover-accent-effect")[0]
            c = video_info_div.find_all("div", class_='Layout-sc-nxg1ff-0 fjGGXR')[0].find_all('div')

            if is_untitled:
                clip_link = self._base_url + video_info_div.find_all("a")[0]['href']
            else:
                clip_link = self._base_url + element_a['href']

            clip_title = "untitled" if is_untitled else element_a.text.strip()
            clip_duration = c[2].text
            clip_views = c[4].text.split(" ")[0]
            clip_created_at = c[6].text

            video["title"] = clip_title
            video["url"] = clip_link
            video["duration"] = clip_duration
            video["views"] = clip_views
            video["created_at"] = clip_created_at

            videos_list.append(video)

        self._parsed_videos = videos_list

    async def parse_until_limit(self, page, video_type, limit=None):
        await asyncio.sleep(3)

        if limit is None:
            while True:
                videos_before_parsing = self.get_parsed_videos()
                await self._parse_page(page, video_type)
                videos_after_parsing = self.get_parsed_videos()

                if len(videos_before_parsing) == len(videos_after_parsing):
                    return None

                await utils.scroll_down(page)

        while len(self._parsed_videos) < limit:
            videos_before_parsing = self.get_parsed_videos()
            await self._parse_page(page, video_type)
            videos_after_parsing = self.get_parsed_videos()

            if len(videos_before_parsing) == len(videos_after_parsing):
                return None

            await utils.scroll_down(page)

        self._parsed_videos = self.get_parsed_videos()[:limit]

    async def _parse_page(self, page, video_type):
        html = await page.content()
        self.parse_twitch_html(html, video_type)


class TwitchHtmlScraper:
    """
    A class to send request and get html response
    """

    def __init__(self):
        self.twitch_base_url = 'https://www.twitch.tv'
        self._browser = None
        self.html_parser = TwitchHtmlParser()

    async def _launch_browser(self):
        self._browser = await pyppeteer.launch(headless=True, defaultViewport={"width": 1920, "height": 1080})

    async def scrape_html(self, username: str, video_type: str, limit: int = None) -> None:
        if video_type not in allowed_video_types:
            raise exceptions.WrongVideoTypeException

        await self._scrape_html(username, video_type, limit)

    async def _scrape_html(self, username, video_type, limit=None) -> None:
        await self._launch_browser()

        videos_url_base_url = self.twitch_base_url + f'/{username}/videos?filter='
        video_type_url = videos_url_base_url + video_type

        if video_type == 'clips':
            video_type_url += '&range=all'

        self._page: Page = await self._browser.newPage()

        await self._page.goto(video_type_url)
        await self.html_parser.parse_until_limit(self._page, video_type, limit=limit)
        await self._browser.close()


class VideoScraper:
    """
    A class to scrape video links from twitch channel.
    """

    def __init__(self):
        self._video_links = dict()
        self._html_scraper = TwitchHtmlScraper()

    async def scrape_videos(self, username: str, videos_type: str, limit: int = None) -> list_of_video_objects:
        """Scrapes videos from twitch.tv user channel depending on type of videos you want to get.


        :param username: twitch username whose videos you want to scrape
        :param videos_type: type of video, like 'clips' or 'highlights'
        :param limit: returned videos count will not be more than passed limit number
        :return: a list, each object is a dictionary with info about specific video
        """
        return await self._scrape_videos(
            username,
            videos_type,
            limit
        )

    async def _scrape_videos(self, username: str, videos_type: str, limit: int = None) -> list_of_video_objects:
        await self._html_scraper.scrape_html(username, videos_type, limit)
        video_objects_list = self._html_scraper.html_parser.get_parsed_videos()

        return video_objects_list
