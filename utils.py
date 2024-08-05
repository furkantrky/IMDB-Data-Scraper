import pandas as pd
import concurrent.futures
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def parse_url_csv(file_path, project_name):
    df = pd.read_csv(file_path)
    df['imdb_id'] = df['url'].str.extract(r'/title/([^/]+)/')
    df.dropna(inplace=True)
    df.drop_duplicates(inplace=True, subset="imdb_id")
    id_list = df["imdb_id"].to_list()
    df.to_csv(f"./imdb_urls_{project_name}_with_id.csv", index=False)
    return id_list


def fetch_and_parse_movie_info(movie_id, imdb, request_interval):
    trial = 0
    while trial < 3:
        try:
            res = imdb.get_by_id(movie_id)
            res = res.replace('null', 'None')
            if '"status": 404' in res:
                trial += 1
                time.sleep(request_interval)
                continue
            return eval(res)
        except Exception as e:
            logger.info(f"Error fetching movie ID {movie_id}: {e}")
            trial += 1
            time.sleep(request_interval)
    logger.info(f"After 3 trials, failed to fetch movie data for ID {movie_id}")
    return None


def process_movie_ids(movie_id_list, final_results, num_workers, imdb, request_interval, project_name):
    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        future_to_id = {executor.submit(fetch_and_parse_movie_info, movie_id, imdb, request_interval): movie_id for movie_id in movie_id_list}

        for future in concurrent.futures.as_completed(future_to_id):
            try:
                data = future.result()
                if data:
                    df = pd.DataFrame([data])
                    final_results = pd.concat([final_results, df], ignore_index=True)
                    results.append(data)

                    # Save current results to CSV and JSON
                    final_results.to_csv(f'./{project_name}_info.csv', index=False)

            except Exception as e:
                logger.info(f"Error processing movie ID {future_to_id[future]}: {e}")

    return final_results


def chunk_movie_id_list(movie_id_list, chunk_size):
    for i in range(0, len(movie_id_list), chunk_size):
        yield movie_id_list[i:i + chunk_size]


def scroll_to_element(driver, by, value):
    """Scroll to an element to ensure it's in view."""
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((by, value))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    time.sleep(1)  # Allow time for the scroll


def click_element(driver, by, value, retries=3):
    """Attempt to click an element with retries and JavaScript click."""
    for attempt in range(retries):
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((by, value))
            )
            scroll_to_element(driver, by, value)
            # Use JavaScript to click if normal click fails
            driver.execute_script("arguments[0].click();", element)
            return True
        except Exception as e:
            logger.info(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(2)
    return False