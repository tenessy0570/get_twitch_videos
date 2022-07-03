import asyncio

import pyppeteer
from bs4 import BeautifulSoup

from . import exceptions
from .constants import allowed_video_types

created_at = str
views_count = str
title = str
duration = str
url = str


class TwitchHtmlParser:
    """
    A class to parse html markup
    """

    def __init__(self):
        self._base_url = "https://www.twitch.tv"
        self._method_for = {"clips": self._parse_twitch_clips}

    def parse_twitch_html_and_get_videos(
            self, html: str, videos_type: str
    ) -> list[
        dict[created_at: str, views_count: str, title: str, duration: str, url: str]
    ]:
        return self._method_for[videos_type](html)

    def _parse_twitch_clips(self, html: str) -> list[dict]:
        soup = BeautifulSoup(html, 'html.parser')

        videos_list = []

        container = soup.find_all('article', class_="Layout-sc-nxg1ff-0 frepDF")

        for article in container:
            video = dict()

            element_a = article.find_all("a")[0]

            clip_title = element_a.text.strip()
            clip_link = self._base_url + element_a['href']

            video_info_div = article.find_all('div', class_="ScWrapper-sc-uo2e2v-0 IbFZu tw-hover-accent-effect")[0]
            c = video_info_div.find_all("div", class_='Layout-sc-nxg1ff-0 fjGGXR')[0].find_all('div')

            clip_duration = c[2].text
            clip_views = c[4].text.split(" ")[0]
            clip_created_at = c[6].text

            video["title"] = clip_title
            video["url"] = clip_link
            video["duration"] = clip_duration
            video["views"] = clip_views
            video["created_at"] = clip_created_at

            videos_list.append(video)

        return videos_list


class TwitchHtmlScraper:
    """
    A class to send request and get html response
    """

    def __init__(self):
        self._html = None
        self.twitch_base_url = 'https://www.twitch.tv'
        self._browser = None

    async def _launch_browser(self):
        self._browser = await pyppeteer.launch(headless=True, defaultViewport={"width": 1920, "height": 1080})

    async def scrape_html(
            self, username: str,
            video_type: str,
            sleep_after_opening_page: int,
            times_to_scroll_down: int,
            sleep_after_scroll: int
    ) -> None:

        if video_type not in allowed_video_types:
            raise exceptions.WrongVideoTypeException

        await self._scrape_html(
            username,
            video_type,
            sleep_after_opening_page,
            times_to_scroll_down,
            sleep_after_scroll
        )

    async def _scrape_html(
            self,
            username,
            video_type,
            sleep_after_opening_page=3,
            times_to_scroll_down=0,
            sleep_after_scroll=2
    ) -> None:
        await self._launch_browser()

        videos_url_base_url = self.twitch_base_url + f'/{username}/videos?filter='
        video_type_url = videos_url_base_url + video_type

        if video_type == 'clips':
            video_type_url += '&range=all'

        self._page = await self._browser.newPage()
        await self._page.goto(video_type_url)

        if isinstance(sleep_after_opening_page, int) and sleep_after_opening_page > 0:
            await asyncio.sleep(sleep_after_opening_page)

        if isinstance(times_to_scroll_down, int) and times_to_scroll_down > 0:
            for _ in range(times_to_scroll_down):
                await self._page.keyboard.down(key='End')
                await asyncio.sleep(sleep_after_scroll)

        html = await self._page.content()

        await self._browser.close()
        self._html = html

    def get_html(self) -> str:
        return self._html


class VideoScraper:
    """
    A class to scrape video links from twitch channel.
    """

    def __init__(self):
        self._video_links = dict()
        self._html_scraper = TwitchHtmlScraper()
        self._html_parser = TwitchHtmlParser()

    async def scrape_videos(
            self,
            username: str,
            videos_type: str,
            sleep_after_opening_page: int = 3,
            times_to_scroll_down: int = 0,
            sleep_after_scroll: int = 2
    ) -> list[dict[
              created_at: str,
              views_count: str,
              title: str,
              duration: str,
              url: str
              ]]:
        """Scrapes videos from twitch.tv user channel depending on type of videos you want to get.


        :param username: twitch username which videos you want to scrape
        :param videos_type: type of video, like 'clips' or 'highlights'
        :param sleep_after_opening_page: how much time to sleep after page was opened
        :param times_to_scroll_down: int, amount of how many times to scroll down to the end of the page. It can
        be used if user has a lot of videos, so you need to render js code using this argument.
        :param sleep_after_scroll: hot much time to sleep after each scroll down
        :return: a list, each object is a dictionary with info about specific video
        """
        return await self._scrape_videos(
            username,
            videos_type,
            sleep_after_opening_page,
            times_to_scroll_down,
            sleep_after_scroll
        )

    async def _scrape_videos(
            self,
            username: str,
            videos_type: str,
            sleep_after_opening_page: int = 3,
            times_to_scroll_down: int = 0,
            sleep_after_scroll: int = 2
    ) -> list[dict]:
        await self._html_scraper.scrape_html(
            username,
            videos_type,
            sleep_after_opening_page,
            times_to_scroll_down,
            sleep_after_scroll
        )
        html = self._html_scraper.get_html()

        video_object_list = self._html_parser.parse_twitch_html_and_get_videos(html, videos_type)
        return video_object_list
