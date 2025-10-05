# Temperature Analysis by Local Climate Zones (LCZ) - Lajeado, RS

Visualization and simulation system for temperature based on Local Climate Zones (LCZ) for the city of Lajeado, Rio Grande do Sul.

## 📋 Overview

This project allows you to:

- **Visualize local climate zones (LCZ)** mapped for Lajeado-RS
- **Retrieve real-time temperature data** via the Meteomatics API
- **Simulate scenarios** of land use change and its thermal impacts
- **Calculate temperature differences** when converting one LCZ to another

## 🌡️ What are Local Climate Zones (LCZ)?

Local Climate Zones are a standardized classification of urban and rural areas based on their thermal properties, developed by Stewart & Oke (2012). The system defines 17 types of zones:

### Urban Zones (LCZ 1–10)

- **LCZ 1–3**: Compact High/Mid/Low-Rise (dense buildings)
- **LCZ 4–6**: Open High/Mid/Low-Rise (spaced buildings)
- **LCZ 7**: Lightweight Low-Rise (light structures)
- **LCZ 8**: Large Low-Rise (large low buildings)
- **LCZ 9**: Sparsely Built (sparse constructions)
- **LCZ 10**: Heavy Industry

### Natural Zones (LCZ 11–17)

- **LCZ 11–13**: Dense/Scattered Trees, Bushes
- **LCZ 14**: Low Plants – **temperature baseline**
- **LCZ 15**: Bare Rock or Paved
- **LCZ 16**: Bare Soil or Sand
- **LCZ 17**: Water

## 🔬 Temperature Calculation Methodology

### Baseline and Thermal Offsets

The calculation methodology is based on the LCZ framework (Stewart & Oke, 2012) and systematic reviews on Urban Heat Island (UHI):

**LCZ 14 (Low Plants)** is used as the baseline (offset = 0°C).

Each LCZ has a **characteristic thermal offset**:

| LCZ | Type                 | Thermal Offset | Scientific Basis                                  |
| --- | -------------------- | -------------- | ------------------------------------------------- |
| 1   | Compact High-Rise    | +2.5°C         | Studies show values between +2.0 and +3.0°C       |
| 2   | Compact Mid-Rise     | +2.8°C         | Identified as the hottest LCZ in multiple studies |
| 3   | Compact Low-Rise     | +2.3°C         | Typical range +2.0 to +2.5°C                      |
| 4   | Open High-Rise       | +1.8°C         | Lower density = lower heating                     |
| 5   | Open Mid-Rise        | +2.0°C         | Significant UHI contributor                       |
| 6   | Open Low-Rise        | +1.5°C         | Moderate heating                                  |
| 7   | Lightweight Low-Rise | +1.2°C         | Light materials = less heat retention             |
| 8   | Large Low-Rise       | +2.2°C         | Large built mass                                  |
| 9   | Sparsely Built       | +0.5°C         | Minimal urban heating                             |
| 10  | Heavy Industry       | +2.6°C         | High anthropogenic heat                           |
| 11  | Dense Trees          | -1.5°C         | Strong cooling via evapotranspiration             |
| 12  | Scattered Trees      | -0.8°C         | Moderate cooling                                  |
| 13  | Bush/Scrub           | -0.3°C         | Slight cooling                                    |
| 14  | Low Plants           | 0.0°C          | **BASELINE**                                      |
| 15  | Bare Rock/Paved      | +2.0°C         | High heat absorption                              |
| 16  | Bare Soil/Sand       | +1.0°C         | Moderate heating                                  |
| 17  | Water                | -2.0°C         | Strong cooling due to high thermal capacity       |

### Calculation Formula

When an area is converted from LCZ A to LCZ B:

```
ΔT = Offset_LCZ_B - Offset_LCZ_A
T_new = T_current + ΔT
```

**Example:**

- Current area: LCZ 3 (Compact Low-Rise), Temperature = 28°C
- Conversion to: LCZ 11 (Dense Trees)
- ΔT = (-1.5°C) - (+2.3°C) = -3.8°C
- T\_new = 28°C - 3.8°C = **24.2°C**

## 🌐 Meteomatics API

### Authentication

The system uses the Meteomatics API to obtain real-time temperature data.

**Endpoint:** `https://api.meteomatics.com`

**Parameters used:**

- `t_2m:C` – Temperature at 2 meters (proxy for urban surface temperature)
- Format: `{datetime}/{parameter}/{location}/json`

### Configuration

1. Obtain credentials at: [https://www.meteomatics.com/](https://www.meteomatics.com/)
2. Configure the `.env` file:

```env
METEOMATICS_USERNAME=your_username
METEOMATICS_PASSWORD=your_password
```

## 🚀 Installation and Usage

### Requirements

- Python 3.8+
- pip

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Copy configuration file
cp .env.example .env

# Edit .env with your Meteomatics credentials
# METEOMATICS_USERNAME=your_username
# METEOMATICS_PASSWORD=your_password
```

### Run

```bash
python app.py
```

Access: [http://localhost:5000](http://localhost:5000)

## 🎯 How to Use the Interface

1. **View LCZs**: The map automatically loads Lajeado’s zones
2. **View Temperature**: Click “Load Temperature Layer” to view thermal data
3. **Select Zone**: Click any LCZ zone on the map
4. **Simulate Change**:
   - Select a new LCZ from the dropdown
   - Click “Calculate Scenario”
   - View the calculated thermal impact
5. **Legend**: Use “Show/Hide Legend” to display all LCZs

## 📊 Project Structure

```
space-apps/
├── app.py                      # Main Flask app
├── config.py                   # Configurations and LCZ constants
├── lcz_processor.py            # KMZ file processing
├── meteomatics_api.py          # Meteomatics API integration
├── temperature_calculator.py   # Thermal difference calculations
├── requirements.txt            # Python dependencies
├── .env.example                # Example configuration file
├── templates/
│   └── index.html              # Web interface
├── static/
│   └── app.js                  # App JavaScript
├── lajeado-result/             # Lajeado LCZ data
│   └── *.kmz                   # KMZ geometry file
└── output/                     # Generated outputs
```

## 📚 Scientific References

### LCZ Framework

1. **Stewart, I. D., & Oke, T. R. (2012).** Local Climate Zones for Urban Temperature Studies. *Bulletin of the American Meteorological Society*, 93(12), 1879–1900.
   - DOI: 10.1175/BAMS-D-11-00019.1
   - Defines LCZ framework and ΔT\_LCZ X–LCZ D methodology

### Systematic Reviews

2. **Yang, J., et al. (2024).** Urban heat dynamics in Local Climate Zones (LCZs): A systematic review. *Building and Environment*.

   - Identified LCZ 2 (Compact Mid-Rise) as the hottest
   - Temperature differences up to 2.62°C between LCZs in Beijing

3. **Mushore, T. D., et al. (2022).** Local Climate Zones to Identify Surface Urban Heat Islands: A Systematic Review. *Remote Sensing*, 15(4), 884.

   - Confirms LCZ-based methodology
   - Validates use of LCZ 14 as baseline

### Case Studies

4. **Li, Y., et al. (2024).** Impact of Local Climate Zones on the Urban Heat and Dry Islands in Beijing. *Journal of Meteorological Research*.

   - Quantifies thermal differences between LCZs
   - Spatial heterogeneity of UHI

5. **Fukuda, S., et al. (2023).** Comparative Analysis of SUHI Based on LCZ for Hiroshima and Sapporo. *Climate*, 11(7), 142.

   - LCZ 10 and LCZ E with temperatures > 40°C
   - Day/night patterns across LCZs

### WUDAPT (World Urban Database and Access Portal Tools)

6. **Demuzere, M., et al. (2019).** WUDAPT Level 0 Training Data.
   - Global framework for LCZ mapping
   - Source: [https://www.wudapt.org/](https://www.wudapt.org/)

## 🔧 API Endpoints

### `GET /api/lcz-data`

Returns GeoJSON data of LCZ zones

### `GET /api/temperature?lat={lat}&lon={lon}`

Gets temperature for a specific point

### `GET /api/temperature-grid`

Retrieves temperature grid for the entire area

### `POST /api/calculate-scenario`

Calculates LCZ change impact

```json
{
  "zone_id": "zone_1",
  "from_lcz": 3,
  "to_lcz": 11,
  "base_temperature": 28.5
}
```

### `GET /api/lcz-classes`

Returns definitions of all LCZ classes

## 📝 Accuracy Notes

- **Thermal offsets** are typical values based on scientific literature
- Local variations may occur due to:
  - Specific meteorological conditions
  - Local topography
  - Proximity to water bodies
  - Real vs. classified vegetation density
- Validation with local measurements is recommended where available

## 🤝 Contributing

Contributions are welcome! Areas of interest:

- Calibration of thermal offsets with local data
- Integration with other temperature sources
- Temporal analysis (historical series)
- Validation with meteorological stations

## 📄 License

This project was developed for scientific and educational analysis.

## 👥 Authors

Developed for Urban Heat Island analysis in Lajeado, RS.

---

**Note**: This system requires valid Meteomatics API credentials to function fully. A free test account can be obtained at [https://www.meteomatics.com/](https://www.meteomatics.com/)
