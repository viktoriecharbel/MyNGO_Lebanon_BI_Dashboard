##### ---- IMPORTS -------- #####
from pathlib import Path
import pandas as pd

#####---- INITIAL FORMATTING & ORIENTATION --- #####
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

####### ----- DIRECTING TO THE CORRECT PATH ------ #######

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "raw" / "population.xlsx"
# print("Looking for file at:", DATA_PATH)
# print("Exists?", DATA_PATH.exists())

#######----- FUNCTIONS  ------ ####
def clean_population_summary():
    """
    Load the district-level table from 'ALL POPULATION SUMMARY', unpivot the 2025/2025 paired columns into a Year column,
    clean dash-as-missing values, and return a tidy long-format dataframe for Power BI use
    """

    df_district = pd.read_excel(DATA_PATH, sheet_name="ALL POPULATION SUMMARY", header = 13)
    df_district = df_district[df_district["Governorate"].notna()].reset_index(drop=True)

    id_cols = ["Governorate", "District"]
    single_cols = [
        "TOTAL IDPs (as of 31 May 2025)",
        "TOTAL People who moved from place of displacement (as of 31 May 2025)",
        "% Change of Population",
        "District impacted by conflict (airstrikes, shelling)",
        "Number of conflict incidents (since Oct 2023)"
    ]

    df_2025 = df_district[id_cols + [
        "TOTAL LEBANESE (2025)", "TOTAL PALESTINIANS (2025)",
        "Palestinian Refugees in Lebanon (PRL) (2025)", "Palestinian Refugees from Syria (PRS) (2025)",
        "TOTAL SYRIANS (2025)", "Migrants (2025)", "TOTAL POPULATION (2025)"
    ] + single_cols].copy()

    df_2026 = df_district[id_cols + [
        'TOTAL LEBANESE (2026)', 'TOTAL PALESTINIANS (2026)', 'Palestinian Refugees in Lebanon (PRL) (2026)',
        'Palestinian Refugees from Syria (PRS) (2026)', 'TOTAL SYRIANS (2026)', 'Migrants (2026)\nPreliminary findings ', 'TOTAL POPULATION (2026)'
    ] + single_cols].copy()

    df_2025 = df_2025.rename(columns={
        "TOTAL LEBANESE (2025)": "Total Lebanese",
        "TOTAL PALESTINIANS (2025)": "Total Palestinians",
        "Palestinian Refugees in Lebanon (PRL) (2025)": "PRL",
        "Palestinian Refugees from Syria (PRS) (2025)": "PRS",
        "TOTAL SYRIANS (2025)": "Total Syrians",
        "Migrants (2025)": "Total Migrants",
        "TOTAL POPULATION (2025)": "Total Population"
    })
    df_2025["Year"] = 2025

    df_2026 = df_2026.rename(columns={
        "TOTAL LEBANESE (2026)": "Total Lebanese",
        "TOTAL PALESTINIANS (2026)": "Total Palestinians",
        "Palestinian Refugees in Lebanon (PRL) (2026)": "PRL",
        "Palestinian Refugees from Syria (PRS) (2026)": "PRS",
        "TOTAL SYRIANS (2026)": "Total Syrians",
        'Migrants (2026)\nPreliminary findings ': "Total Migrants",
        "TOTAL POPULATION (2026)": "Total Population"
    })
    df_2026["Year"] = 2026

    full_df = pd.concat([df_2025, df_2026])
    full_df= full_df.reset_index(drop = True)

    full_df["TOTAL IDPs (as of 31 May 2025)"] = pd.to_numeric(
        full_df["TOTAL IDPs (as of 31 May 2025)"].replace(r"^\s*-\s*$", pd.NA, regex=True)
    )
    full_df["TOTAL People who moved from place of displacement (as of 31 May 2025)"] = pd.to_numeric(
        full_df["TOTAL People who moved from place of displacement (as of 31 May 2025)"].replace(r"^\s*-\s*$", pd.NA, regex=True)
    )

    full_df = full_df.rename(columns={
        "TOTAL IDPs (as of 31 May 2025)": "Total IDPs",
        "TOTAL People who moved from place of displacement (as of 31 May 2025)": "Total Returnees",
        "District impacted by conflict (airstrikes, shelling)": "District Impacted by Conflict",
        "Number of conflict incidents (since Oct 2023)": "Conflict Incidents"
    })

    full_df = full_df[
    ["Governorate", "District", "Year", "Total Lebanese", "Total Palestinians", "PRL", "PRS",
         "Total Syrians", "Total Migrants", "Total Population", "Total IDPs", "Total Returnees",
         "% Change of Population", "District Impacted by Conflict", "Conflict Incidents"
    ]]

    return full_df

##### ---- CREATING CLEAN POWERBI READY CSVs -----######
if __name__ == "__main__":
    population_summary_clean = clean_population_summary()

    OUTPUT_PATH = BASE_DIR / "data" / "clean" / "population_summary_clean.csv"
    population_summary_clean.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved to {OUTPUT_PATH}")
