import multiprocessing
import argparse
import os

from settings.default import (
    CPD_YFINANCE_OUTPUT_FOLDER,
    CPD_DEFAULT_LBW,
)


def main(lookback_window_length: int, n_workers=None):
    if not os.path.exists(CPD_YFINANCE_OUTPUT_FOLDER(lookback_window_length)):
        os.mkdir(CPD_YFINANCE_OUTPUT_FOLDER(lookback_window_length))

    tickers = [x.strip(".csv") for x in os.listdir("data/yfinance") if x[-3:] == "csv"]
    if n_workers is None:
        n_workers = len(tickers)

    all_processes = {
        ticker: f'python3 -m examples.cpd_yfinance "{ticker}" "{os.path.join(CPD_YFINANCE_OUTPUT_FOLDER(lookback_window_length), ticker + ".csv")}" "1990-01-01" "2022-08-18" "{lookback_window_length}"'
        for ticker in tickers
    }

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
        args = parser.parse_known_args()[0]
        return [
            args.lookback_window_length,
            args.n_workers
        ]

    main(*get_args())
