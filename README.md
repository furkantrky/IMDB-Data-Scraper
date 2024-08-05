# IMDB Scraper

This project contains a set of scripts to scrape and process IMDB data. The scripts perform the following tasks:

1. **Fetch URLs** from an IMDB search page.
2. **Extract movie IDs** from the fetched URLs.
3. **Retrieve detailed movie information** using the extracted IDs.

## Scripts Overview

### 1. `args.py`

Defines command-line arguments for the scripts.

### 2. `utils.py`
Contains utility functions for parsing URLs, processing movie IDs, and interacting with web elements.

Functions:

- `parse_url_csv(file_path, project_name)`: Parses a CSV file to extract and clean IMDB IDs.
- `fetch_and_parse_movie_info(movie_id, imdb, request_interval)`: Fetches and parses movie information by ID.
- `process_movie_ids(movie_id_list, final_results, num_workers, imdb, request_interval, project_name)`: Processes a list of movie IDs and saves results to CSV.
- `chunk_movie_id_list(movie_id_list, chunk_size)`: Yields chunks of movie IDs for batch processing.
- `scroll_to_element(driver, by, value)`: Scrolls to a web element.
- `click_element(driver, by, value, retries=3)`: Clicks a web element with retries.

### 3. `main.py`
The main script that uses Selenium to scrape IMDB, extract URLs, and process movie information.

## Requirements

- selenium==4.23.0
- chromedriver_autoinstaller==0.6.4
- pandas==2.2.2
- beautifulsoup4==4.12.3
- tqdm==4.66.4
- PyMovieDb==0.0.9

## How to Run

1. **Set up the environment** and install dependencies as described above.
2. **Run the main script**:

    ```sh
    python main.py --url "https://www.imdb.com/search/title/?title_type=tv_series,tv_miniseries" --click_count 50 --project_name "series" --num_workers 4 --request_interval 3
    ```

    - `--url`: IMDB search URL to scrape.
    - `--click_count`: Number of times to click the "Show 50 more" button.
    - `--project_name`: Prefix for output files.
    - `--num_workers`: Number of concurrent threads for processing.
    - `--request_interval`: Interval between requests in seconds.

The script will output the scraped movie URLs and detailed movie information to CSV files.

## Acknowledgements

Special thanks to the [PyMovieDb](https://github.com/SensiPeeps/PyMovieDB) project for providing the IMDb API integration used in this script.