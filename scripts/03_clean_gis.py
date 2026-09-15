from pathlib import Path
import json

####### ----- DIRECTING TO THE CORRECT PATH ------ #######

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "raw" / "admin_boundaries" / "lbn_admin3_em.geojson"

###### ----- FUNCTIONS -------- ####
def clean_admin_boundaries():
    """
    Load the admin3 boundaries GeoJSON, remove junk 'Conflict' placeholder features,
    trim each feature's properties to relevant fields for joining to the other datasets in PowerBI
    :return: cleaned GeoJSON structure (dictionary) cleaned_geojson
    """
    with open(DATA_PATH, encoding="utf-8") as f:
        gj=json.load(f)

    real_features = [f for f in gj["features"] if f["properties"]["adm3_name"] != "Conflict"]

    keep_keys = ["adm3_name", "adm3_pcode", "adm2_name", "adm2_pcode",
                 "adm1_name", "adm1_pcode", "area_sqkm", "center_lat", "center_lon"]

    cleaned_features = []
    for feature in real_features:
        cleaned_properties = {key: feature["properties"][key] for key in keep_keys}
        cleaned_feature = {
            "type": feature["type"],
            "properties": cleaned_properties,
            "geometry": feature["geometry"]
        }
        cleaned_features.append(cleaned_feature)

    cleaned_geojson = {
        "type": gj["type"],
        "name": gj["name"],
        "crs": gj["crs"],
        "features": cleaned_features
    }

    return cleaned_geojson


####### ----- CREATING CLEAN GEOJSON ------ ####
if __name__ == "__main__":
    cleaned_geojson = clean_admin_boundaries()

    OUTPUT_PATH = BASE_DIR / "data" / "clean" / "lbn_admin3_clean.geojson"
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(cleaned_geojson, f, ensure_ascii=False)

    print(f"Saved to {OUTPUT_PATH}")

