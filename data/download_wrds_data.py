import wrds
import pandas as pd
from datetime import datetime
import pickle
from settings.default import WRDS_PRICE_PATH, WRDS_CONST_PATH


def main():
    db = wrds.Connection()
    constituents = db.get_table("comp_na_daily_all", "idxcst_his").set_index("gvkey")
    security = db.get_table("comp_na_daily_all", "security").set_index("gvkey")
    data = constituents.join(security[["tic", "cusip", "dldtei"]])
    data = data[data["gvkeyx"] == "000208"].reset_index()  # 208=Nasdaq 100
    dates = pd.date_range(data["from"].min(), datetime.today())
    components = pd.DataFrame(index=dates, columns=data["gvkey"].unique())

    for i in data.index:
        components.loc[data.loc[i, "from"]:data.loc[i, "thru"], data.loc[i, "gvkey"]] = True
    components = components.asfreq("BM", how="last").dropna(axis=1, how='all')
    components = components.reindex(dates, method='pad').dropna(axis=1, how='all').dropna(how='all')

    gvkeys = ", ".join([f"'{x}'" for x in components.columns])
    sql = f"select gvkey, datadate, tic, prccd, prchd, prcod, ajexdi, trfd  from comp.secd where gvkey in ({gvkeys})" \
          f" and datadate >= '1995-01-31'"

    prices = db.raw_sql(sql)
    prices["adjclose"] = prices["prccd"] / prices["ajexdi"]
    pickle.dump(prices, open(WRDS_PRICE_PATH, "wb"))
    pickle.dump(components, open(WRDS_CONST_PATH, "wb"))


if __name__ == "__main__":
    main()
