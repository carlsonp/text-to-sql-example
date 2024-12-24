#!/usr/bin/env python3
import pandas as pd
from sqlalchemy import create_engine
import glob, os

if not os.path.isfile("/data/sqlitedatabase.db"):

    engine = create_engine("sqlite:///data/sqlitedatabase.db")

    for fullpath in glob.glob(f"/data/*.csv"):
        print(f"Running on {fullpath}")
        filename = os.path.basename(fullpath)
        df = pd.read_csv(fullpath)
        print(df.info())
        # Write the DataFrame to the database, inferring table structure
        df.to_sql(filename.removesuffix(".csv"), engine, if_exists="replace", index=False)
        print(f"Loaded table: {filename.removesuffix(".csv")} - into SQLite")

print("Finished loading data into SQLite")