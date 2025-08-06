# Kor File Viewer

A Streamlit application for viewing and mapping Kor measurement data from CSV export files.

## Features

- 📁 **File Upload**: Drag and drop CSV files directly into the browser
- 📊 **Data Display**: View parsed measurement data in an interactive table
- 🗺️ **Interactive Map**: Visualize measurement locations on an interactive map
- 📈 **Data Summary**: See key statistics about your measurements
- 🔍 **Data Validation**: Automatic handling of various file encodings and formats

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -e .
   ```
   or if using uv:
   ```bash
   uv sync
   ```

## Usage

1. Start the Streamlit app:
   ```bash
   streamlit run app.py
   ```

2. Open your browser and navigate to the provided URL (usually `http://localhost:8501`)

3. Upload a Kor measurement CSV file using the file picker

4. View the parsed data and interactive map

## Expected File Format

The app expects Kor Measurement File Export exactly as it is exported from the Kor desktop software.

## Dependencies

- `pandas` - Data manipulation and analysis
- `plotly` - Interactive plotting and mapping
- `streamlit` - Web application framework

## Development

The app consists of:
- `main.py` - Core parsing and mapping functions
- `app.py` - Streamlit web interface