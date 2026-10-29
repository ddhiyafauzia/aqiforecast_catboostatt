## Air Quality Index (AQI) Forecasting in DKI Jakarta with Categorical Boosting and Attention Mechanism

In densely populated urban areas like DKI Jakarta, air pollution—especially fine particulate matter (PM2.5)—poses serious health risks, contributing to bronchitis, asthma, heart disease, stroke, and even death [1]. The interplay of multiple pollutants, weather variability, traffic emissions, and industrial activities complicates air quality dynamics [2], [13], prompting recent research to treat pollution as a spatiotemporal problem rather than isolated measurements [3], [14]. This approach captures both temporal patterns (e.g., hourly or daily changes) and spatial relationships across monitoring stations. Traditional statistical methods often fail to model these complex, nonlinear patterns, whereas machine learning models like Categorical Boosting handle high-dimensional structured data efficiently using histogram-based binning and a leaf-wise growth strategy [4], [15]. However, Categorical Boosting alone may not effectively prioritize temporal or environmental features unless explicitly guided. To address this, attention mechanisms—originally from natural language processing—are now applied in time series forecasting to emphasize critical features such as sudden weather shifts or pollution spikes [5], [6], [16], [17], [18]. Combining Categorical Boosting with attention improves interpretability and predictive accuracy [6], [9], [10], [19], [20], though many models remain limited to low-resolution data or single-station inputs [7], [21]. This study proposes a hybrid attention–Categorical Boosting framework to model multivariate spatiotemporal correlations of PM2.5 in DKI Jakarta, using hourly climate data from five satellite-derived sources and pollutant data (PM2.5, PM10, NO₂, SO₂, CO, O₃) from five ground stations (2020–2024). An attention mechanism is applied after preprocessing and temporal segmentation to highlight key variables at each timestep, followed by Categorical Boosting to model nonlinear interactions. The method enhances interpretability and forecasting performance, offering insights for data-driven policymaking and urban air quality management.

## Business Understanding
This research provides accurate assessments of PM2.5 levels across urban areas, supporting strategies to control pollution from industry and transportation by integrating pollutant concentrations with climate conditions that often exceed who’s recommended limits, the system can capture both rapid fluctuations and long-term seasonal patterns. The forecasting ability directly supports:

- Emission Management: where local governments can temporarily restrict heavy trucks or industrial activities when high pollution levels are predicted
- Public Health Advisory: enabling early alerts when pm2.5 is expected to exceed 5 μg/m³ annually, potentially reducing hospital visits for respiratory problems by 3–5% and saving jakarta rp 50–100 billion in healthcare costs each year [3]
- Sustainable Urban Planning: here long-term predictions guide low-emission zones, green spaces, and relocation of sensitive facilities by linking spatio-temporal correlations between pollutants and weather elements, this approach enhances prediction accuracy and strengthens data-driven decision-making for fast-response systems in Jakarta’s most vulnerable areas.
  
By linking spatiotemporal correlations between pollutants and weather elements, this approach enhances prediction accuracy and strengthens decision-making for fast-response systems in Jakarta’s most vulnerable areas.

## Run steamlit app
```
streamlit run app.py

```

## Github Repositories
```
https://github.com/ddhiyafauzia/aqiforecast_catboostatt  

```

## AQI Forecast Dashboard with CatBoost-Att
```
For running the dashboard online: https://aqi-forecast-catboostatt.streamlit.app/

```


## Copyright © Fauzia Dhiyaa' Farros 2026 - Universitas Sugeng Hartono
