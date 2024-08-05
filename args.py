import argparse


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--url",
        type=str,
        default="https://www.imdb.com/search/title/?title_type=tv_series,tv_miniseries",
        help="The search url on imdb that you get other urls.",
    )
    parser.add_argument(
        "--click_count",
        type=int,
        default=50,
        help="How many times that the script will click the 50 more button",
    )
    parser.add_argument(
        "--project_name",
        type=str,
        default="series",
        help="A prefix that will add to the output filenames.",
    )
    parser.add_argument(
        "--num_workers",
        type=int,
        default=4,
        help="Number of threads that will work.",
    )
    parser.add_argument(
        "--request_interval",
        type=int,
        default=3,
        help="Total time to process num_workers requests",
    )

    args = parser.parse_args()
    return args