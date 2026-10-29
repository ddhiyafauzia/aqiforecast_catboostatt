"""Narrative text, schema tables and references shown across the dashboard."""
from __future__ import annotations

INTRODUCTION = """
In densely populated urban areas like DKI Jakarta, air pollution—especially fine particulate matter
(PM2.5)—poses serious health risks, contributing to bronchitis, asthma, heart disease, stroke, and
even death [1]. The interplay of multiple pollutants, weather variability, traffic emissions, and
industrial activities complicates air quality dynamics [2], [13], prompting recent research to treat
pollution as a spatiotemporal problem rather than isolated measurements [3], [14]. This approach captures
both temporal patterns (e.g., hourly or daily changes) and spatial relationships across monitoring stations.

Traditional statistical methods often fail to model these complex, nonlinear patterns, whereas machine
learning models like Categorical Boosting handle high-dimensional structured data efficiently using
histogram-based binning and a leaf-wise growth strategy [4], [15]. However, Categorical Boosting alone may
not effectively prioritize temporal or environmental features unless explicitly guided. To address this,
attention mechanisms—originally from natural language processing—are now applied in time series forecasting
to emphasize critical features such as sudden weather shifts or pollution spikes [5], [6], [16], [17], [18].
Combining Categorical Boosting with attention improves interpretability and predictive accuracy
[6], [9], [10], [19], [20], though many models remain limited to low-resolution data or single-station
inputs [7], [21].

This study proposes a hybrid attention–Categorical Boosting framework to model multivariate spatiotemporal
correlations of PM2.5 in DKI Jakarta, using hourly climate data from five satellite-derived sources and
pollutant data (PM2.5, PM10, NO₂, SO₂, CO, O₃) from five ground stations (2020–2024). An attention mechanism
is applied after preprocessing and temporal segmentation to highlight key variables at each timestep,
followed by Categorical Boosting to model nonlinear interactions. The method enhances interpretability and
forecasting performance, offering insights for data-driven policymaking and urban air quality management.
"""

HOME_FACTS = (
    ("AQI stations", "5", "Jakarta Environmental Agency"),
    ("Meteorological stations", "4", "NOAA hourly network"),
    ("Pollutants", "6", "PM2.5 · PM10 · SO₂ · CO · O₃ · NO₂"),
    ("Study period", "2020–2024", "Hourly resolution"),
)

WHO_REFERENCE = (
    ("PM2.5", "< 5 μg/m³ (annual)"),
    ("PM10", "< 15 μg/m³ (annual)"),
    ("SO₂", "< 40 μg/m³ (10-min)"),
    ("CO", "< 4 mg/m³ (daily)"),
    ("O₃", "< 100 μg/m³ (8-hour)"),
    ("NO₂", "< 10 μg/m³ (annual)"),
    ("Max", "Depends on pollutant type"),
    ("Category", "Good"),
    ("temperature", "20–25 °C"),
    ("dew_point_temperature", "Depends on air temperature"),
    ("relative_humidity", "40–60%"),
    ("wind_speed", "0–15 m/s"),
    ("wind_direction", "None"),
    ("precipitation", "Seasonal dependent"),
    ("precipitation_24_hour", "Seasonal dependent"),
)

DATASET_AQI = """
The dataset comprises the **Air Pollution Standard Index (ISPU)** collected from **five Air Quality
Monitoring Stations** operated by the Jakarta Environmental Agency.

📂 Public data: [Jakarta Smart City Portal](https://satudata.jakarta.go.id/)
"""

DATASET_METEO = """
The dataset also includes **hourly meteorological data** from NOAA (temperature, precipitation, humidity,
latitude/longitude and elevation), collected from four meteorological stations.

📂 Public data: [Global Historical Climatology Network – Hourly](https://www.ncei.noaa.gov/access/search/data-search/global-historical-climatology-network-hourly)
"""

BUSINESS_UNDERSTANDING = """
This research provides accurate assessments of PM2.5 levels across urban areas, supporting strategies to
control pollution from industry and transportation. By integrating pollutant concentrations with climate
conditions that often exceed WHO-recommended limits, the system can capture both rapid fluctuations and
long-term seasonal patterns.
"""

BUSINESS_PILLARS = (
    ("🚛 Emission Management",
     "Local governments can temporarily restrict heavy trucks or industrial activities when high pollution "
     "levels are predicted."),
    ("🩺 Public Health Advisory",
     "Early alerts when PM2.5 is expected to exceed 5 μg/m³ (annual guideline) can reduce hospital visits for "
     "respiratory problems by 3–5% and save Jakarta Rp 50–100 billion in healthcare costs each year [3]."),
    ("🏙️ Sustainable Urban Planning",
     "Long-term predictions guide low-emission zones, green spaces, and the relocation of sensitive facilities."),
)

BUSINESS_CLOSING = (
    "By linking **spatiotemporal correlations between pollutants and weather elements**, this approach enhances "
    "prediction accuracy and strengthens decision-making for **fast-response systems** in Jakarta's most "
    "vulnerable areas."
)

AQI_SCHEMA = (
    ("periode_data", "int64"), ("tanggal", "datetime64[ns]"), ("PM10", "float64"), ("SO2", "float64"),
    ("CO", "float64"), ("O3", "float64"), ("NO2", "float64"), ("Max", "float64"), ("Critical", "object"),
    ("Category", "object"), ("Station", "object"), ("PM2.5", "float64"), ("sulfur_dioksida", "float64"),
    ("karbon_monoksida", "float64"), ("ozon", "float64"), ("nitrogen_dioksida", "float64"), ("bulan", "float64"),
)
AQI_ROWS = 6966

METEO_SCHEMA = (
    ("station_name", "object"), ("date", "datetime64[ns]"), ("latitude", "float64"), ("longitude", "float64"),
    ("elevation", "float64"), ("temperature", "float64"), ("dew_point_temperature", "float64"),
    ("relative_humidity", "float64"), ("wind_speed", "float64"), ("wind_direction", "float64"),
    ("precipitation", "float64"), ("precipitation_24_hour", "float64"), ("sea_level_pressure", "float64"),
    ("visibility", "float64"),
)
METEO_ROWS = 99231

CORRELATION_NOTES = """
- **Positive correlation (r > 0)** → the value tends to **increase** as the other parameter increases.
- **Negative correlation (r < 0)** → the value tends to **decrease** as the other parameter increases.

**A. Inter-pollutant (AQI vs AQI)**
- **PM2.5 – PM10 (r = 0.69):** strong positive — shared sources such as vehicular emissions, combustion and dust.
- **CO – O₃ (r = 0.38):** moderate positive — CO acts as a precursor in ozone formation.
- **CO – NO₂ (r = 0.32):** moderate — both originate from combustion and traffic.
- **PM2.5 – NO₂ (r = 0.25):** weak to moderate — urban and industrial activity.
- **PM10 – NO₂ (r = 0.23):** weak to moderate — mixed particulate sources.

**B. Inter-meteorological**
- **Temperature – Relative humidity (r = –0.89):** very strong negative — warmer air holds relatively less moisture.
- **Dew point – Relative humidity (r = 0.62):** strong positive — both reflect moisture content.
- **Temperature – Wind speed (r = 0.45):** moderate positive — warm air enhances convective movement.
- **Pressure – Sea-level pressure (r ≈ 0.40–0.50):** moderate — stable atmospheric pressure relationships.

**C. Pollutant–meteorology**
- **CO – Temperature (r = 0.32):** CO rises with temperature (enhanced photochemical reactions).
- **PM2.5 – Visibility (r = 0.25):** fine particles scatter light and reduce visibility.
- **PM10 – Visibility (r = 0.23):** coarse particles show a similar effect.
- **SO₂ – Visibility (r = 0.18):** slight reduction due to aerosol formation.
- **PM10 – Temperature (r = 0.17):** weak positive — possible dust resuspension in warmer conditions.

*Stronger correlations (|r| > 0.6) indicate direct or inverse environmental relationships; weaker ones suggest
indirect or complex interactions.*
"""

MODEL_INSIGHTS = {
    "LightGBM Attention": """
- **Overview:** Hybrid tree-based model enhanced with attention and adaptive weighting.
- **Strengths:** High interpretability, low error (RMSE < 0.5 for all windows) and stable across time steps.
- **Weaknesses:** Slightly higher training time than linear models.
- **Inference:** Predictions stay very close to the true AQI (≈113), showing strong generalization.
- **Best use:** Short- to mid-range forecasting with high accuracy and explainability.
""",
    "Linear Regression": """
- **Overview:** Baseline model for comparison.
- **Strengths:** Fastest training; very stable across window lengths.
- **Weaknesses:** Limited in capturing complex temporal or non-linear dependencies.
- **Performance:** RMSE decreases with longer windows, showing smoother trend learning.
- **Best use:** Quick baselines or limited computational power.
""",
    "Lasso Regression": """
- **Overview:** Linear model with L1 regularization to prevent overfitting.
- **Strengths:** Slightly better stability and sparsity control than plain linear regression.
- **Weaknesses:** Still limited in learning temporal sequences; training time grows quickly with window length.
- **Performance:** Excellent at longer windows (RMSE ≈ 0.002 at 48 h).
- **Best use:** Feature selection or simple AQI estimation pipelines.
""",
    "FNN": """
- **Overview:** Simple deep learning model without temporal memory.
- **Strengths:** Models non-linear dependencies better than linear models.
- **Weaknesses:** Struggles with long-term sequence dependencies.
- **Performance:** Error rises at longer windows, indicating loss of temporal understanding.
- **Best use:** Small-scale AQI patterns or non-sequential data.
""",
    "CNN–LSTM": """
- **Overview:** CNN for feature extraction combined with LSTM for temporal learning.
- **Strengths:** Able to capture spatiotemporal correlations in AQI data.
- **Weaknesses:** High training time and less stable on small datasets.
- **Performance:** RMSE stays high (> 2.5) across all windows; may need tuning or regularization.
- **Best use:** Large, multi-station AQI datasets with spatial variability.
""",
    "GRU–LSTM": """
- **Overview:** Hybrid sequential model combining GRU efficiency and LSTM accuracy.
- **Strengths:** Learns temporal dependencies effectively.
- **Weaknesses:** Computationally heavy and slow to train on long windows.
- **Performance:** RMSE 0.04–0.22; best at 1 h and 48 h windows.
- **Best use:** Medium-term AQI fluctuations with complex temporal dependencies.
""",
    "CatBoost": """
- **Overview:** Gradient boosting optimized for categorical and numerical data.
- **Strengths:** Near-perfect accuracy (RMSE ≤ 0.010 for all windows) with fast training.
- **Weaknesses:** May overfit if the dataset is too small.
- **Performance:** Most stable and efficient among all models.
- **Best use:** Tabular AQI forecasting and real-time deployment.
""",
    "Transformer": """
- **Overview:** Sequence-to-sequence model based on self-attention.
- **Strengths:** Captures long-range dependencies effectively.
- **Weaknesses:** Needs large datasets and tuning; only 1 h and 8 h windows were evaluated.
- **Performance:** RMSE < 0.1 on both evaluated windows.
- **Best use:** Advanced forecasting and large-scale AQI prediction pipelines.
""",
}

FINDINGS = (
    ("🏆 Best overall", "CatBoost", "Lowest RMSE and fast convergence."),
    ("⚖️ Most balanced", "LightGBM Attention", "Good trade-off between accuracy and efficiency."),
    ("📏 Strong baselines", "Linear · Lasso", "Highly efficient with acceptable accuracy."),
    ("🔁 Best sequential", "GRU–LSTM", "Effective in medium-range forecasting."),
    ("🧠 Most advanced", "Transformer", "Strong potential for long-range dependencies."),
    ("🛠️ Needs work", "CNN–LSTM", "Unstable on small datasets."),
)

METRIC_DEFINITIONS = (
    ("RMSE", "Root Mean Squared Error — lower means higher accuracy."),
    ("MAE", "Mean Absolute Error — average absolute difference between prediction and truth."),
    ("MAPE", "Mean Absolute Percentage Error — error as a percentage of actual values."),
    ("train_time", "Total training time in seconds — a proxy for computational cost."),
)

REFERENCES = (
    "Zhang, B., Chen, W., Li, M., Guo, X., Zheng, Z., and Yang, R., “MGAtt-LSTM: A multi-scale spatial correlation prediction model of PM2.5 concentration based on multi-graph attention,” *Environmental Modelling & Software*, vol. 179, p. 106095, 2024.",
    "Ye, Y., Cao, Y., Dong, Y., and Yan, H., “A graph neural network and Transformer-based model for PM2.5 prediction through spatiotemporal correlation,” *Environmental Modelling and Software*, vol. 191, p. 106501, 2025.",
    "Borah, J., Kumar, S., Nadzir, M. S. M., Cayetano, M. G., Ghayvat, H., Majumdar, S., and Kumar, N., “AiCareBreath: IoT-Enabled Location-Invariant Novel Unified Model for Predicting Air Pollutants to Avoid Related Respiratory Disease,” *IEEE Internet of Things Journal*, vol. 11, no. 8, pp. 14625–14633, 2024.",
    "Iskandaryan, D., Ramos, F., and Trilles, S., “A set of deep learning algorithms for air quality prediction applications,” *Software Impacts*, vol. 16, p. 100365, 2023.",
    "Doush, I. A., Sultan, K., Alsaber, A., Alkandari, D., and Abdullah, A., “Enhanced Jaya optimization for improving multilayer perceptron neural network in urban air quality prediction,” *Journal of Intelligent Systems*, vol. 33, no. 1, pp. 1–32, 2024.",
    "Gond, A. K., Jamal, A., and Verma, T., “Developing a machine learning model using satellite data to predict the Air Quality Index (AQI) over Korba Coalfield, Chhattisgarh (India),” *Atmospheric Pollution Research*, vol. 16, no. 2, Article 102398, 2025.",
    "Kunjir, G. M., Tikle, S., Das, S., Karim, M., Roy, S. K., and Chatterjee, U., “Assessing particulate matter (PM2.5) concentrations and variability across Maharashtra using satellite data and machine learning techniques,” *Discover Sustainability*, vol. 6, no. 1, Article 10823, 2025.",
    "Li, R., Hu, Y., Xu, Z., Shao, X., and Huo, Y., “Predicting the complex variation characteristics of equipment heat dissipation in office buildings via CNN-LSTM-ATT, multiple regression, and similar day models,” *Building and Environment*, vol. 280, p. 113051, 2025.",
    "Shih, D. H., Chung, F. I., Wu, T. W., Wang, B. H., and Shih, M. H., “Advanced Trans-BiGRU-QA fusion model for atmospheric mercury prediction,” *Mathematics*, vol. 12, no. 22, Article 3547, 2024.",
    "Wang, S.-J., Huang, B.-J., and Hu, M.-H., “A deep learning-based air quality index prediction model using LSTM and reference stations: A real application in Taiwan,” in *Proc. 33rd Int. Telecommun. Netw. Appl. Conf. (ITNAC)*, Melbourne, Australia, 2023, pp. 204–209.",
    "Shen, J., Liu, Q., and Feng, X., “Hourly PM2.5 concentration prediction for dry bulk port clusters considering spatiotemporal correlation: A novel deep learning blending ensemble model,” *Journal of Environmental Management*, vol. 337, p. 117795, 2024.",
    "Zhang, J., and Li, S., “Air quality index forecast in Beijing based on CNN-LSTM multi-model,” *Chemosphere*, vol. 308, p. 136180, 2022.",
    "Santiko, I., Soeprobowati, T. R., Surarso, B., and Tahyudin, I., “Campus websites' information quality measurement model and potential students' interest prediction,” *TEM Journal*, vol. 14, no. 2, pp. 1845–1859, 2025.",
    "Wicaksana, H. S., Kusumaningrum, R., and Gernowo, R., “Determining community happiness index with transformers and attention-based deep learning,” *IAES International Journal of Artificial Intelligence*, vol. 13, no. 2, pp. 1753–1761, 2024.",
    "Triyono, L., Gernowo, R., and Prayitno, “MoNetViT: an efficient fusion of CNN and transformer technologies for visual navigation assistance with multi query attention,” *Frontiers in Computer Science*, vol. 7, 1510252, 2025.",
    "Koesuma, S., et al., “Tropical cyclone-related extreme rainfall and its impact under solar radiation management (SRM) in eastern Indonesia region,” in *EGU General Assembly*, Vienna, Austria, Apr. 2024, EGU24-20960.",
    "Koesuma, S., et al., “Analysis of extreme rainfall of tropical cyclone using solar radiation management and ERA5 data in eastern Indonesia,” *Geographia Technica*, vol. 20, no. 1, pp. 298–312, 2025.",
    "Hakim, D. K., Gernowo, R., and Nirwansyah, A. W., “Flood prediction with time series data mining: Systematic review,” *Natural Hazards Research*, vol. 4, no. 2, pp. 194–220, 2023.",
    "Usman, C. D., Widodo, A. P., Adi, K., and Gernowo, R., “Rainfall prediction model in Semarang city using machine learning,” *Indonesian Journal of Electrical Engineering and Computer Science*, vol. 30, no. 2, pp. 1224, 2023.",
    "Gernowo, R., Purbasari, A., Widada, S., and Purboyo, W., “Combination of flood models with weather research and forecast based on extreme rainfall for hazard mitigations,” *Journal of Physics: Conference Series*, vol. 1524, no. 1, 012144, 2020.",
    "Santiko, I., et al., “Traditional-enhance-mobile-ubiquitous-smart: Model innovation in higher education learning style classification using multidimensional and machine learning methods,” *Journal of Applied Data Science*, vol. 6, no. 1, pp. 753–772, 2025.",
    "Utomo, A. P., Purwanto, P., and Surarso, B., “Latest algorithms in machine and deep learning methods to predict retention rates and dropout in higher education: A literature review,” *E3S Web of Conferences*, vol. 448, 02034, 2023.",
    "Zhou, Y., Chen, H., Li, J., Wu, Y., Wu, J., and Chen, L., “ST-Attn: Spatial-temporal attention for crowd flow prediction,” in *Proc. IEEE Int. Conf. Data Mining Workshops (ICDMW)*, Nov. 2019, pp. 609–614.",
)
