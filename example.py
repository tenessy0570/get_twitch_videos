import asyncio
import pprint

from twitch_scraping import scraping


async def example():
    scraper = scraping.VideoScraper()
    video_objects = await scraper.scrape_videos(
        username='tenessy_fjxcsd',
        videos_type='clips',
        limit=10  # You can pass None
    )

    pprint.pprint(video_objects)
    print(len(video_objects))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(example())
