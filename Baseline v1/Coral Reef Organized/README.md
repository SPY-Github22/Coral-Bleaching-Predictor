# Coral Bleaching Predictor — Organized Pipeline

This folder contains **only the files that were actually used** to build the final coral bleaching predictor model, arranged in the order they were executed.

---

## Pipeline Overview

```
Raw Data → Prep Images → Process pH/SST/Spatial/Bleaching → Combine → Train Model → Deploy Web App
```

---

## Step-by-Step Breakdown

### Step 0 — Raw Data
Source data files (too large to copy here, see `README.txt` inside):
- **Allen Coral Atlas**: `reefextent.gpkg`, `benthic.gpkg`, `boundary.geojson`
- **Copernicus pH**: `.nc` files (area-averaged + trend)
- **SST Images**: `sst_images/` (monthly heatmap screenshots)
- **Bleaching Images**: `coral_bleaching_images/` (NOAA alert level images)
- **Ocean Acidity CSV**: `ocean-acidity_fig-1.csv`

---

### Step 1 — Data Preparation (renaming + color extraction)

| Sub-step | Script | Purpose |
|----------|--------|---------|
| 1a | `rename.py` | Renames SST frame images (`frame_0051.png` → `october_2006.png`) |
| 1b | `dont_mind.py` | Renames bleaching images from URL-based names to `month_year.png` |
| 1c | `rbgdivision.py` | Extracts RGB-to-temperature mapping from the SST color scale image |

---

### Step 2 — Spatial Data Processing (Allen Coral Atlas)
| Script | Purpose |
|--------|---------|
| `perfecto copy.py` | Joins reef extent + benthic data, clips to boundary, calculates reef area → `processed_spatial_data.gpkg` |
| `visualization.py` | Creates interactive plotly choropleth map → `interactive_reef_area_map.html` |
| `insta_map.py` | Quick-launch wrapper for the interactive map |

---

### Step 3 — pH Data Pipeline (Copernicus)

| Sub-step | Script | Input → Output |
|----------|--------|----------------|
| 3a | `coper-2.py` | Combines area-averaged pH + trend `.nc` files → `combined_pH_and_trend_subset.nc` |
| 3b | `monthly-coper-debug copy.py` | Interpolates yearly pH to monthly resolution → `monthly_global_ph.nc` |
| 3c | `nc2csv.py` | Converts `monthly_global_ph.nc` → monthly CSV files in `monthly_csvs/` |
| 3d | `cleaner.py` | Removes 'time' column from CSVs → cleaned files in `full_clean/` |

---

### Step 4 — SST Data Extraction
| Script | Purpose |
|--------|---------|
| `final_sst_data.py` | Extracts temperature values from SST images using **KDTree** nearest-neighbor color matching with a detailed 38-point color scale → CSVs in `output_csv/` |

---

### Step 5 — Bleaching Alert Extraction
| Script | Purpose |
|--------|---------|
| `bleaching_extraction.py` | Extracts bleaching alert levels from NOAA images using RGB color matching → CSVs in `bleaching_csv/` |

---

### Step 6 — Data Combination
| Script | Purpose |
|--------|---------|
| `final_COMBINE.PY` | Spatially matches and merges SST + pH + Bleaching data by lat/lon using **cKDTree** → combined CSVs in `final_out/` |

Each output CSV contains: `Latitude, Longitude, Temperature(C), pH, Alert Level`

---

### Step 7 — Model Training
| Script | Purpose |
|--------|---------|
| `trainer_1.py` | Trains **RandomForest Classifier** on combined data, aggregates by region, saves model as `coral_bleaching_predictor.pkl` (tuple format: `(model, alert_level_mapping)`) |

**Features**: Region_Lat, Region_Lon, Avg_Temperature, Avg_pH  
**Target**: Most common Alert Level per region  
**Output**: `model/coral_bleaching_predictor.pkl`

---

### Step 8 — Web App (Flask Deployment)
| File | Purpose |
|------|---------|
| `main.py` | Final Flask app with templates (frame1-4.html), supports point & area prediction |
| `integration_main.py` | Earlier integration version with render_template routing |
| `templates/` | HTML templates (frame1-4.html) for the web interface |
| `static/` | CSS files for styling |

**How it works**: User inputs lat/lon + SST + pH → model predicts coral bleaching Alert Level

---

## Files NOT Included (experimental/superseded)

These files from the original project were **not used** in the final pipeline:

| File | Reason |
|------|--------|
| `copernicus.py` | Template with placeholder paths, never run |
| `monthly-coper.py` | Only generates pH map visualizations |
| `monthly-coper-debug.py` | Earlier version (uses deprecated `freq='M'`) |
| `visual_coper.py` | pH visualization only |
| `sst.py`, `sst2.py`, `sst3.py` | Superseded SST extraction iterations |
| `sst_cv.py` | Different approach: image classification model, not used |
| `script.py` | Early RF prototype with hardcoded SST/pH values |
| `perfecto.py` | Earlier version of `perfecto copy.py` |
| `new_script.py` | Different approach: acidity predictor model |
| `combination.py`, `final1.py` | Different approach: GB + CNN image-based models |
| `predictive model.py` | Different approach: RF + CNN year predictor |
| `final_regen.py` | Superseded SST extraction with color ranges |
| `remove_black.py` | Land removal from SST CSVs (output not used in final pipeline) |
| `WhiteGod.py`, `WhiteGod2.py` | Earlier Flask web app iterations |
| `visualiser_1.py` | Tkinter GUI for predictions (superseded) |
| `visualiser_browser.py` | Earlier Flask web app with folium map |
| `TRAINER.PY` | Produces `coral_bleaching_rf.pkl` (dict format, not used by web app) |
| `ITS DONE.PY` | Similar to TRAINER.PY (dict format model) |
| `TEST.PY`, `please_work.py` | Earlier model trainers producing wrong pkl format |
| `retrain.py` | Retraining script (simpler version of trainer_1.py) |
