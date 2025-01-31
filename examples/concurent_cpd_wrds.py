import multiprocessing
import argparse
import os
import pickle
import pandas as pd

from settings.default import (
    CPD_WRDS_OUTPUT_FOLDER,
    CPD_DEFAULT_LBW,
    WRDS_PRICE_PATH,
    WRDS_CONST_PATH,
    ONEDRIVE_CPD_WRDS_OUTPUT_FOLDER
)


def filter_tickers(tickers, dir, id_type):
    files = os.listdir(dir)
    res = []
    if files:
        files = [x[:-4] for x in files if x[-3:] == "csv"]

    for x in tickers:
        include = True
        include &= x not in files if files else True
        include &= x is not None
        include &= x.isalpha() if include and id_type == "tic" else True

        if include:
            res.append(x)

    return res


def main(lookback_window_length: int, n_workers=None, latest_tickers=False, onedrive=False, id_type="gvkey"):

    save_dir = ONEDRIVE_CPD_WRDS_OUTPUT_FOLDER(lookback_window_length) if onedrive else CPD_WRDS_OUTPUT_FOLDER(lookback_window_length)

    if not os.path.exists(save_dir):
        os.mkdir(save_dir)

    constituents = pickle.load(open(WRDS_CONST_PATH, "rb"))
    prices = pickle.load(open(WRDS_PRICE_PATH, "rb"))
    constituents.index = pd.to_datetime(constituents.index)

    if latest_tickers:
        tickers = list(constituents.iloc[-1].dropna().index)
    else:
        tickers = list(constituents.columns)

    tickers = filter_tickers(tickers, save_dir, id_type)

    all_processes = {}
    for ticker in tickers:
        valid_dates = constituents[ticker].dropna()
        valid_dates = valid_dates[valid_dates].index
        start, end = valid_dates[0].strftime("%Y-%m-%d"), valid_dates[-1].strftime("%Y-%m-%d")

        price_dates = prices.loc[prices[id_type] == ticker, ["datadate", "adjclose"]].dropna()["datadate"]
        first_price_dt = price_dates.min().strftime("%Y-%m-%d")
        last_price_dt = price_dates.max().strftime("%Y-%m-%d")

        start = max(first_price_dt, start)
        end = min(end, last_price_dt)

        all_processes[ticker] = f'python -m examples.cpd_wrds "{ticker}" ' \
                                f'"{os.path.join(save_dir, ticker + ".csv")}" ' \
                                f'"{start}" "{end}" "{lookback_window_length}" ' \
                                f'"{id_type}"'

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
            "latest_tickers",
            metavar="t",
            type=bool,
            nargs="?",
            default=False,
            help="Whether to run CPD only on current index constituents"
        )
        parser.add_argument(
            "onedrive",
            metavar="o",
            type=bool,
            nargs="?",
            default=False,
            help="Whether to save files on OneDrive"
        )
        parser.add_argument(
            "id_type",
            metavar="i",
            type=str,
            nargs="?",
            default="gvkey",
            help="Type of ticker identifier"
        )
        args = parser.parse_known_args()[0]
        return [
            args.lookback_window_length,
            args.n_workers,
            args.latest_tickers,
            args.onedrive,
            args.id_type
        ]


    main(*get_args())
