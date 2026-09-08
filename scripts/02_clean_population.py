##### ---- IMPORTS -------- #####
from pathlib import Path
import pandas as pd

#####---- INITIAL FORMATTING & ORIENTATION --- #####
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

####### ----- DIRECTING TO THE CORRECT PATH ------ #######

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "raw" / "population.xlsx"

#######----- FUNCTIONS  ------ ####
def clean_population_summary():
    """
    Load the district-level table from 'ALL POPULATION SUMMARY', unpivot the 2025/2026 paired columns into a Year column,
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


def clean_age_pyramid_sheet(sheet_name, header_row, total_col, female_col, male_col, nationality, extra_cols=None):
    """
    Load one nationality's age/sex pyramid sheet (district-level), and reshape the age-band columns from wide format
    into tidy long format.

    :param sheet_name: str
    :param header_row: int, starting from which header to reach district level data;
    :param total_col: str, name of the column concerning the total population;
    :param female_col: str, name of the column regarding all female;
    :param male_col: str, name of the column regarding all male;
    :param nationality: str, label identifying which population group this sheet represents (e.g. "Lebanese")
    :param extra_cols: list of str, optional extra numeric columns specific to this nationality;
    :return: long_df
    """
    extra_cols = extra_cols or []

    df = pd.read_excel(DATA_PATH, sheet_name=sheet_name, header=header_row)
    df.columns = df.columns.str.strip()
    df = df[df["Governorate"].notna() & df["District"].notna()].reset_index(drop=True)

    df["Nationality"] = nationality

    id_cols = ['Governorate', 'District', 'Nationality', 'Total Population', 'Distribution %', 'Total Female', 'Total Male'] + extra_cols
    age_cols = ['Age\n 0 - 4', '5 - 9', '10 - 14', '15 - 19', '20 - 24', '25 - 29', '30 - 34', '35 - 39', '40 - 44',
                '45 - 49', '50 - 54', '55 - 59', '60 - 64', '65 - 69', '70 - 74', '75 - 79', '80 - 84', '85 and above']

    numeric_cols = [total_col, female_col, male_col] + extra_cols + age_cols

    nan_counts = df[numeric_cols].isna().sum()
    nan_counts = nan_counts[nan_counts > 0]
    if not nan_counts.empty:
        print(f"{sheet_name}: NaN values filled with 0 -\n{nan_counts}")

    df[numeric_cols] = df[numeric_cols].fillna(0).astype(int)
    df=df.rename(columns={
        total_col: "Total Population",
        female_col: "Total Female",
        male_col: "Total Male"
    })
    long_df = df.melt(
        id_vars=id_cols,
        value_vars=age_cols,
        var_name="Age Group",
        value_name="Population"
    )

    long_df["Age Group"] = long_df["Age Group"].str.replace("Age", "", regex=False)
    long_df["Age Group"] = long_df["Age Group"].str.replace(" and above", "+", regex=False)
    long_df["Age Group"] = long_df["Age Group"].str.strip()
    long_df["Age Group"] = long_df["Age Group"].str.replace(r"\s*-\s*", "-", regex=True)

    return long_df
##### ---- CREATING CLEAN POWERBI READY CSVs -----######

if __name__ == "__main__":
    population_summary_clean = clean_population_summary()

    leb_long = clean_age_pyramid_sheet(sheet_name="LEBANESE", header_row=13, total_col="TOTAL LEBANESE",
                                       female_col="All Lebanese Female", male_col="All Lebanese Male",
                                       nationality= "Lebanese", extra_cols = None)

    syr_long = clean_age_pyramid_sheet(sheet_name="SYRIAN", header_row=13, total_col="Syrian_Est",
                                       female_col="All Syrians Female", male_col="All Syrians Male",
                                       nationality= "Syrian", extra_cols = None)

    pal_long = clean_age_pyramid_sheet(sheet_name="PALESTINIAN", header_row=13, total_col="TOTAL PALESTINIANS",
                                       female_col="All Palestinian Female", male_col="All Palestinian Male",
                                       nationality="Palestinian",
                                       extra_cols=['PRL - Camps Population', 'PRL - Gatherings Population', 'Total PRL',
                                                   'PRS in Camps', 'PRS outside Camps', 'Total PRS'])

    combined_pyramid = pd.concat([leb_long, syr_long, pal_long], ignore_index=True)

    population_summary_clean.to_csv(BASE_DIR / "data" / "clean" / "population_summary_clean.csv", index=False)
    combined_pyramid.to_csv(BASE_DIR / "data" / "clean" / "population_age_pyramid_clean.csv", index=False)
    print("Saved: population_summary_clean.csv, population_age_pyramid_clean.csv")

