#### --------- CONFIG (imports, paths, constants)------ ####
from pathlib import Path
import pandas as pd

pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "data" / "clean"


PROJECTS = [
    {
        "ProjectID": "P01",
        "ProjectName": "Community-Based Child Protection in Akkar",
        "Sector": "Child Protection",
        "Donor": "DonorA",
        "StartDate": "2025-01-01",
        "EndDate": "2026-12-31"
    },{
        "ProjectID": "P02",
        "ProjectName": "Community-Based GBV Prevention and Response in Hermel",
        "Sector": "GBV",
        "Donor": "DonorA",
        "StartDate": "2026-01-01",
        "EndDate": "2027-12-31"
    },{
        "ProjectID": "P03",
        "ProjectName": "Education Project in Bekaa",
        "Sector": "Education",
        "Donor": "DonorB",
        "StartDate": "2025-06-01",
        "EndDate": "2026-06-30"
    },{
        "ProjectID": "P04",
        "ProjectName": "Community-Based Child Protection in Bekaa",
        "Sector": "Child Protection",
        "Donor": "DonorC",
        "StartDate": "2026-02-01",
        "EndDate": "2027-02-28"
    },{
        "ProjectID": "P05",
        "ProjectName": "Community-Based Child Protection in Hermel",
        "Sector": "Child Protection",
        "Donor": "DonorD",
        "StartDate": "2026-07-01",
        "EndDate": "2028-12-31"
    },{
        "ProjectID": "P06",
        "ProjectName": "Community-Based GBV Response and Prevention in South Lebanon",
        "Sector": "GBV",
        "Donor": "DonorD",
        "StartDate": "2026-07-01",
        "EndDate": "2028-12-31"
    },{
        "ProjectID": "P07",
        "ProjectName": "Community-Based GBV Response and Prevention in Bekaa",
        "Sector": "GBV",
        "Donor": "DonorA",
        "StartDate": "2026-05-01",
        "EndDate": "2027-05-31"
    },{
        "ProjectID": "P08",
        "ProjectName": "Community-Based GBV Response and Prevention in Akkar",
        "Sector": "GBV",
        "Donor": "DonorD",
        "StartDate": "2025-01-01",
        "EndDate": "2026-12-31"
    },{
        "ProjectID": "P09",
        "ProjectName": "Education Project in South Lebanon",
        "Sector": "Education",
        "Donor": "DonorD",
        "StartDate": "2025-01-01",
        "EndDate": "2027-12-31"
    },{
        "ProjectID": "P10",
        "ProjectName": "MHPSS in South Lebanon",
        "Sector": "MHPSS",
        "Donor": "DonorD",
        "StartDate": "2025-05-01",
        "EndDate": "2027-05-31"
    },{
        "ProjectID": "P11",
        "ProjectName": "MHPSS in Akkar",
        "Sector": "MHPSS",
        "Donor": "DonorD",
        "StartDate": "2025-09-01",
        "EndDate": "2026-09-30"
    },{
        "ProjectID": "P12",
        "ProjectName": "Child Protection in South Lebanon",
        "Sector": "Child Protection",
        "Donor": "DonorD",
        "StartDate": "2025-01-01",
        "EndDate": "2027-12-31"
    },
]

INDIVIDUALS = "Individuals"
SERVICES = "Services"

SECTOR_INDICATORS = {
    "Child Protection":
        [
            ("# children accessing case management", INDIVIDUALS),
            ("# case management follow-up visits conducted", SERVICES),
            ("# child-friendly space activity sessions held", SERVICES),
            ("# parenting sessions held", SERVICES)
        ],
    "GBV":
        [
            ("# individuals accessing GBV case management", INDIVIDUALS),
            ("# case management follow-up visits conducted", SERVICES),
            ("# individuals receiving Cash for Protection", INDIVIDUALS),
            ("# cash distribution follow-ups conducted", SERVICES)
        ],
    "Education":
        [
            ("# students attending daily classes", INDIVIDUALS),
            ("# students receiving in-kind educational items", INDIVIDUALS),
            ("# remedial classes conducted", SERVICES),
            ("# monitoring missions conducted to educational facilities", SERVICES)
        ],
    "MHPSS":
        [
            ("# individuals accessing individual therapy sessions", INDIVIDUALS),
            ("# group PSS activities conducted", SERVICES),
            ("# individuals receiving group PSS sessions", INDIVIDUALS),
            ("# individuals referred to specialised mental health services", INDIVIDUALS)
        ]
}

##### ------ FUNCTIONS------- ###
def build_projects():
    """
    Creates dataframe containing project details (Project ID, Project Names, Sector, Donor, StartDate, EndDate)
    :return: df_projects
    """
    df_projects = pd.DataFrame(PROJECTS)
    df_projects["StartDate"] = pd.to_datetime(df_projects["StartDate"])
    df_projects["EndDate"] = pd.to_datetime(df_projects["EndDate"])

    return df_projects

def build_indicators(df_projects):
    """
     Creates a dataframe with one row per project indicator: IndicatorID, ProjectID, IndicatorText and CountingUnit
    :return: df_indicators
    """
    templates = pd.DataFrame(
        [(sector, text, unit)
         for sector, items in SECTOR_INDICATORS.items()
         for text, unit in items],
        columns=["Sector", "IndicatorText", "CountingUnit"],
    )

    df=df_projects[["ProjectID", "Sector"]].merge(templates, on="Sector", how="left")

    df["IndicatorID"] = (
        df["ProjectID"] + "-I"
        + (df.groupby("ProjectID").cumcount() + 1).astype(str).str.zfill(2)
    )
    df_indicators = df[["IndicatorID", "ProjectID", "IndicatorText", "CountingUnit"]]
    return df_indicators

###### ----- VALIDATION FUNCTIONS ----- ######

def validate(df_projects, df_indicators):
    """Stop script if the tables break any of the following rules."""
    checks= [
        (df_projects["ProjectID"].is_unique, "Duplicate ProjectID"),
        (df_indicators["IndicatorID"].is_unique, "Duplicate IndicatorID"),
        (df_projects["Sector"].isin(list(SECTOR_INDICATORS)).all(), "Sector with no indicator template."),
        (df_indicators["IndicatorText"].notna().all(), "Missing IndicatorText"),
        ((df_projects["EndDate"] > df_projects["StartDate"]).all(), "EndDate is not after StartDate"),
        ((df_projects["StartDate"].dt.is_month_start).all(), "StartDate is not the 1st of a month"),
        ((df_projects["EndDate"].dt.is_month_end).all(), "EndDate is not a month end"),
        (df_indicators["CountingUnit"].isin([INDIVIDUALS, SERVICES]).all(), "Unknown CountingUnit"),
        (not df_indicators.duplicated(subset=["ProjectID", "IndicatorText"]).any(),
              "Repeated indicator within a project")
    ]
    failures = [message for passed, message in checks if not passed]
    if failures:
        raise ValueError("Validation failed:\n- " + "\n- ".join(failures))

######------SCRIPT-------#####
if __name__ == "__main__":
    df_projects=build_projects()
    df_indicators=build_indicators(df_projects)
    validate(df_projects, df_indicators)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    tables= {"projects": df_projects, "indicators": df_indicators}
    for name, df in tables.items():
        df.to_csv(OUTPUT_DIR / f"{name}.csv", index=False)
        print(f"Saved {name}.csv ({len(df)} rows)")
