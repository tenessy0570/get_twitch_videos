import pprint

from scraping import scrape

scraper = scrape.VideoScraper()
video_links = scraper.scrape_videos('redshell', 'archives')

print(len(video_links))
pprint.pprint(video_links)
