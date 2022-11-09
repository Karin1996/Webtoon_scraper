# Webtoon Scraper

Scraping original webtoons from the official webtoon website and writing the information to a JSON and CSV file for ***analyzation purposes***.

- Change variable ```amount_to_scrape``` in ```webscraper.py``` for the amount of webtoons to scrape
- Executing the script will start the scraping. Results will be visible in ```webtoon_information.json``` and ```webtoon_information.csv``` after the scraping is done
- Import results in a spreadsheet program, use it in a script with Matplotlib or something else you prefer

<sub> * A Webtoon can have 2 genres, but only 1 is visible on the frontend. Data therefore might not be entirely accurate. </sub>
