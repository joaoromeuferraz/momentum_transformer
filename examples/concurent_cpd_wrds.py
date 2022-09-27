import multiprocessing
import argparse
import os
import pickle
import pandas as pd

from settings.default import (
    CPD_WRDS_OUTPUT_FOLDER,
    CPD_DEFAULT_LBW,
    WRDS_PRICE_PATH,
    WRDS_CONST_PATH
)


def filter_repeated_tickers(tickers, dir):
    files = os.listdir(dir)
    if files:
        files = [x[:-4] for x in files if x[-3:] == "csv"]
        return [x for x in tickers if x not in files]
    return tickers


def main(lookback_window_length: int, n_workers=None, id_type="gvkey"):
    if not os.path.exists(CPD_WRDS_OUTPUT_FOLDER(lookback_window_length)):
        os.mkdir(CPD_WRDS_OUTPUT_FOLDER(lookback_window_length))
    prices = pickle.load(open(WRDS_PRICE_PATH, "rb"))
    tickers = list(prices[id_type].unique())
    tickers = filter_repeated_tickers(tickers, CPD_WRDS_OUTPUT_FOLDER(lookback_window_length))

    constituents = pickle.load(open(WRDS_CONST_PATH, "rb"))
    constituents.index = pd.to_datetime(constituents.index)

    all_processes = {}
    for ticker in tickers:
        valid_dates = constituents[ticker].dropna()
        valid_dates = valid_dates[valid_dates].index
        start, end = valid_dates[0].strftime("%Y-%m-%d"), valid_dates[-1].strftime("%Y-%m-%d")
        all_processes[ticker] = f'python -m examples.cpd_wrds "{ticker}" ' \
                                f'"{os.path.join(CPD_WRDS_OUTPUT_FOLDER(lookback_window_length), ticker + ".csv")}" ' \
                                f'"{start}" "{end}" "{lookback_window_length}"'

    if n_workers is None:
        n_workers = len(tickers)

    if n_workers > 1:
        process_pool = multiprocessing.Pool(processes=n_workers)
        process_pool.map(os.system, list(all_processes.values()))
    else:
        for ticker, process in all_processes.items():
            print(ticker)
            os.system(process)


if __name__ == "__main__":
    def get_args():
        """Returns settings from command line."""

        parser = argparse.ArgumentParser(
            description="Run changepoint detection module for all tickers"
        )
        parser.add_argument(
            "lookback_window_length",
            metavar="l",
            type=int,
            nargs="?",
            default=CPD_DEFAULT_LBW,
            help="CPD lookback window length",
        )
        parser.add_argument(
            "n_workers",
            metavar="n",
            type=int,
            nargs="?",
            default=None,
            help="Number of workers (multiprocessing)",
        )
        parser.add_argument(
            "id_type",
            metavar="i",
            type=str,
            nargs="?",
            default="gvkey",
            help="Type of ticker provided"
        )
        args = parser.parse_known_args()[0]
        return [
            args.lookback_window_length,
            args.n_workers,
            args.id_type
        ]


    main(*get_args())
