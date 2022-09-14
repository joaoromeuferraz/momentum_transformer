import yfinance as yf
import quandl
from settings.default import API_KEY
import datetime as dt
import argparse
import os

DEPTH = 1


def main(tickers=None, index_symbol=None, start=None, end=None):
    quandl.ApiConfig.api_key = API_KEY

    if not os.path.exists(os.path.join("data", "yfinance")):
        os.mkdir(os.path.join("data", "yfinance"))

    if tickers is None:
        tickers = quandl.get_table("NDAQ/IC", paginate=True)
        if index_symbol is not None:
            tickers = tickers[tickers["index_symbol"] == index_symbol]
        tickers = list(tickers.component_symbol.unique())

    data = yf.download(tickers, start=start, end=end)

    for t in tickers:
        data["Adj Close"][[t]].rename(columns={t: "Settle"}).dropna().to_csv(
            os.path.join("data", "yfinance", f"{t}.csv")
        )


if __name__ == "__main__":
    pass
