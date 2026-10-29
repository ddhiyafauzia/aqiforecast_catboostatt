# AQI Intel — Spatiotemporal AQI Forecasting Dashboard (DKI Jakarta)

© 2026 Fauzia Dhiyaa' Farros - Universitas Sugeng Hartono

## Run
```bash
pip install -r requirements.txt
streamlit run app.py
```
Put `aqi_meteo.csv` and the `meteorology/` folder next to `app.py`.
Optional: drop `university_logo.png`, `jktlogo.png`, `jktimage.jpeg` next to `app.py` to use your real logos/photo
(otherwise the bundled USH emblem and animated skyline are used).

## Test
```bash
python -m unittest discover -s tests -t .      # or: pip install -r requirements-dev.txt && pytest
```

## Layout
- `aqi/config.py, data.py, stats.py, models.py, content.py` — pure logic (fully unit-tested, no UI)
- `aqi/theme.py, ui.py, hero.py, assets.py` — design tokens, components, interactive hero, cached assets
- `aqi/pages/` — one module per page · `app.py` — entry point · `assets/` — logo, USH emblem, skyline (SVG)
