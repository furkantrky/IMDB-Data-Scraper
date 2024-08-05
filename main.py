import logging
import time
import pandas as pd
from tqdm.auto import tqdm
from bs4 import BeautifulSoup
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from PyMovieDb import IMDB
from utils import parse_url_csv, chunk_movie_id_list, process_movie_ids, click_element
from args import get_arguments

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.getLogger("urllib3").setLevel(logging.ERROR)

caps = DesiredCapabilities.CHROME
caps['goog:loggingPrefs'] = {'browser': 'OFF', 'driver': 'OFF'}

args = get_arguments()
url_list = []
click_count = 0
imdb = IMDB()
num_workers = args.num_workers
request_interval = args.request_interval
final_results = pd.DataFrame()


# Automatically install the appropriate ChromeDriver
chromedriver_autoinstaller.install()
# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--log-level=3')
chrome_options.add_argument('--window-size=1200x600')
chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')


logger.info("*" * 20)
logger.info("Start Fetching The URLs From The Search URL")
logger.info("*" * 20)
# Initialize the WebDriver
driver = webdriver.Chrome(options=chrome_options)

try:
    # URL of the page you want to scrape
    url = args.url

    # Load the page
    driver.get(url)
    time.sleep(2)  # Wait for the page to load

    # Click the "Show 50 more" button multiple times to load more results
    while True:
        if click_element(driver, By.CSS_SELECTOR, 'span.ipc-see-more__text'):
            click_count += 1  # Increment the click counter
            logger.info(f"Clicked '50 more' button {click_count} times.")
            time.sleep(3)  # Wait for the new content to load
            if click_count == args.click_count:
                break
        else:
            logger.info("No more '50 more' buttons found or another error occurred.")
            break

    # Get the page source after loading all results
    downloaded = driver.page_source

    # Parse the page content with BeautifulSoup
    soup = BeautifulSoup(downloaded, 'html.parser')

    # Extract all links
    links = soup.find_all('a', href=True)

    # Filter and construct full URLs
    movie_urls = [f"https://www.imdb.com{link['href']}" for link in links if '/title/' in link['href']]

    # Remove duplicates
    movie_urls = list(set(movie_urls))

    # Print the extracted URLs
    for movie_url in movie_urls:
        url_list.append(movie_url)

finally:
    # Close the browser
    driver.quit()

df = pd.DataFrame({"url":url_list})
df.drop_duplicates(inplace=True)
logger.info(f"Total URLs found: {len(df)}")
df.to_csv(f"./imdb_urls_{args.project_name}.csv", index=False)


logger.info("*" * 20)
logger.info("Start Processing Movie Ids In Batchs For Getting Movie Info")
logger.info("If fetching a movie info fails it will otomatically be try 3 times.")
logger.info("*" * 20)

movie_id_list = parse_url_csv(f"./imdb_urls_{args.project_name}.csv", args.project_name)

for batch in tqdm(chunk_movie_id_list(movie_id_list, num_workers), total=(len(movie_id_list) // num_workers) + 1, desc="Processing batches"):
    final_results = process_movie_ids(batch, final_results, num_workers, imdb, request_interval, args.project_name)
    # Wait before processing the next batch
    time.sleep(request_interval)

logger.info("Processing complete.")
