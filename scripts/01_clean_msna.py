#### --------- IMPORTS ------ ####
from pathlib import Path
import pandas as pd

#####---- INITIAL FORMATTING & ORIENTATION --- #####
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

####### ----- DIRECTING TO THE CORRECT PATH ------ #######

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "raw" / "msna.xlsx"

#########----- FUNCTIONS -------- #######
def clean_sector_sheet(sheet_name):
    """
    Load one MSNA sector sheet and reshape it from wide format (one column per disaggregation) into tidy long format
    (one row per indicator x disaggregation combination).
    :param sheet_name: str, name of the MSNA sector sheet to load adn clean
    :return: long_df, tidy long-format dataframe for this sector
    """
    df = pd.read_excel(DATA_PATH, sheet_name=sheet_name, header=1)
    raw = pd.read_excel(DATA_PATH, sheet_name=sheet_name, header=None, nrows=2)

    disagg_labels = raw.iloc[0].ffill()
    col_to_disagg_type = dict(zip(df.columns, disagg_labels))

    id_cols = ['key', 'sector', 'Indicator ID', 'Indicator', 'Question', 'Answers/Label']
    value_cols = [c for c in df.columns if c not in id_cols]
    long_df = df.melt(
        id_vars= id_cols,
        value_vars= value_cols,
        var_name= "disagg_value",
        value_name= "value"
    )

    long_df["disagg_type"] = long_df["disagg_value"].map(col_to_disagg_type)
    long_df = long_df.dropna(subset=["value"])
    long_df = long_df[["sector", "Indicator ID", "Indicator", "Question", "Answers/Label", "disagg_type", "disagg_value", "value", "key"]]

    return long_df

####### ------ CREATING A CLEAN POWERBI READY CSV ------######
if __name__ == "__main__":
    xl = pd.ExcelFile(DATA_PATH)
    NON_SECTOR_SHEETS = ['README', 'Coverage', 'TOC']
    SECTOR_SHEETS = [s for s in xl.sheet_names if s not in NON_SECTOR_SHEETS]

    all_sectors = []

    for sheet in SECTOR_SHEETS:
        try:
            cleaned = clean_sector_sheet(sheet)
            all_sectors.append(cleaned)
            print(f"{sheet}: OK, {cleaned.shape[0]} rows")
        except Exception as e:
            print(f"{sheet}: FAILED - {e}")

    if not all_sectors:
        raise RuntimeError("No sector sheets were cleaned successfully - check errors above.")
    msna_clean = pd.concat(all_sectors, ignore_index=True)

    ##### ---- SAVING FILE -----######
    OUTPUT_PATH = BASE_DIR / "data" / "clean" / "msna_clean.csv"
    msna_clean.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved to {OUTPUT_PATH}")
