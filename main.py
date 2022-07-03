import asyncio
import pprint

from twitch_scraping import scraping


async def main():
    scraper = scraping.VideoScraper()
    video_links = await scraper.scrape_videos(
        username='redshell',
        videos_type='clips',
        sleep_after_opening_page=3,
        times_to_scroll_down=4,
        sleep_after_scroll=2
    )

    pprint.pprint(video_links)
    print(len(video_links))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
