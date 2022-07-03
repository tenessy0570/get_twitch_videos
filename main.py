import asyncio
import pprint

from twitch_scraping import scraping


async def main():
    scraper = scraping.VideoScraper()
    video_links = await scraper.scrape_videos(
        username='tenessy_fjxcsd',
        videos_type='clips',
        limit=1
    )

    pprint.pprint(video_links)
    print(len(video_links))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
