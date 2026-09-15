import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

msna = pd.read_csv( BASE_DIR / "data" / "clean" / "msna_clean.csv" )

non_numeric = msna[pd.to_numeric(msna["value"], errors = "coerce").isna()]
print(non_numeric.shape)
print(non_numeric.head(20))