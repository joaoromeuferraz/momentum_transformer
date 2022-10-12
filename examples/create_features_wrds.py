import argparse
from typing import List
import pickle
import pandas as pd
import os

from data.pull_data import pull_wrds_sample_data

from settings.default import (
    CPD_WRDS_OUTPUT_FOLDER,
    FEATURES_WRDS_FILE_PATH,
    ONEDRIVE_CPD_WRDS_OUTPUT_FOLDER,
    WRDS_PRICE_PATH
)
from mom_trans.data_prep import (
    deep_momentum_strategy_features,
    include_changepoint_features,
)


def main(
        tickers: List[str],
        lookback_window_length: int or List[int],
        output_name: str,
        id_type="gvkey",
        onedrive=False
):
    if isinstance(lookback_window_length, int):
        lookback_window_length = [lookback_window_length]

    prices = pickle.load(open(WRDS_PRICE_PATH, "rb"))
    prices["datadate"] = pd.to_datetime(prices["datadate"])

    features = pd.concat(
        [
            deep_momentum_strategy_features(pull_wrds_sample_data(ticker, prices, id_type)).assign(
                ticker=ticker
            )
            for ticker in tickers
        ]
    )

    features.date = features.index
    features.index.name = "Date"

    if lookback_window_length:
        cpd_dir = ONEDRIVE_CPD_WRDS_OUTPUT_FOLDER if onedrive else CPD_WRDS_OUTPUT_FOLDER
        for lbw in lookback_window_length:
            features = include_changepoint_features(
                features, cpd_dir(lbw), lbw
            )

    if not os.path.exists(FEATURES_WRDS_FILE_PATH):
        os.mkdir(FEATURES_WRDS_FILE_PATH)

    features.to_csv(os.path.join(FEATURES_WRDS_FILE_PATH, output_name + ".csv"))


if __name__ == "__main__":
    def get_args():
        """Returns settings from command line."""
        parser = argparse.ArgumentParser(description="Run changepoint detection module")
        # parser.add_argument(
        #     "cpd_module_folder",
        #     metavar="c",
        #     type=str,
        #     nargs="?",
        #     default=CPD_QUANDL_OUTPUT_FOLDER_DEFAULT,
        #     # choices=[],
        #     help="Input folder for CPD outputs.",
        # )
        parser.add_argument(
            "lookback_window_length",
            metavar="l",
            type=int or list,
            nargs="?",
            default=[],
            # choices=[],
            help="Lookback window(s)",
        )
        parser.add_argument(
            "output_name",
            metavar="o",
            type=str,
            nargs="?",
            default="features",
            # choices=[],
            help="Output file name for csv.",
        )
        parser.add_argument(
            "id_type",
            metavar="i",
            type=str,
            nargs="?",
            default="gvkey",
            # choices=[],
            help="Ticker identifier type",
        )
        parser.add_argument(
            "onedrive",
            metavar="-e",
            type=bool,
            nargs="*",
            default=False,
            # choices=[],
            help="Whether data directory is in OneDrive",
        )

        args = parser.parse_known_args()[0]
        ticker_dir = ONEDRIVE_CPD_WRDS_OUTPUT_FOLDER if args.onedrive else CPD_WRDS_OUTPUT_FOLDER

        lbw = args.lookback_window_length
        first_lbw = lbw if isinstance(lbw, int) else lbw[0]
        tickers = [x[:-4] for x in ticker_dir(first_lbw)]

        return (
            tickers,
            lbw,
            args.output_name,
            args.id_type,
            args.onedrive
        )


    main(*get_args())
