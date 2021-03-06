import pandas as pd
from sqlalchemy import create_engine


def sort_csv(filename):
    df = pd.read_csv(f"./{filename}")
    username = df.iloc[0, 0]
    df["Username"] = username
    df["Datetime"] = pd.to_datetime(df.Datetime).dt.strftime("%d-%m-%Y %H:%S").astype(str)
    df.drop(axis=0, index=[0, len(df.index) - 1], inplace=True)
    df.drop(["Beginning Balance", "Ending Balance", "Disclaimer"], axis=1, inplace=True)
    df.update(df[["Amount (fee)", "Statement Period Venmo Fees", "Year to Date Venmo Fees"]].fillna(0))
    df.update(df[["Destination", "Funding Source"]].fillna(""))
    df["Amount (total)"] = df["Amount (total)"].str.strip("$()")
    df["Note"] = df["Note"].str.capitalize()
    df.columns = df.columns.str.replace(r"(\()|(\))", "", regex=True).str.strip(" ").str.replace(" ", "_").str.lower()
    df = df.rename({"from": "sender", "id": "transaction_id", "type": "transaction_type", "to": "recipient"}, axis=1)

    df.sort_values('datetime')
    return df


def create_database(datasource, dbname: str = "transactions") -> None:
    """
    Generates a database from the datasource
    :param datasource: CSV Filename or Pandas Dataframe
    :param dbname: database file and table name
    :return: None
    """
    if type(datasource) is str:
        df = sort_csv(filename=datasource)
    elif type(datasource) is pd.DataFrame:
        df = datasource
    else:
        raise ValueError(f"{datasource} must be a CSV filename or Pandas.DataFrame")

    s = create_engine(f"sqlite:///database/{dbname}.db")
    df.to_sql(name=dbname, con=s, if_exists="replace", index=True)


if __name__ == "__main__":
    create_database("./ACTS Challenge 1 Sample.csv")
