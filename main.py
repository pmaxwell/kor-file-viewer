import io

import pandas as pd
import plotly.express as px


def rename_columns(col):
    if "LATITUDE" in col:
        return "Lat"
    elif "LONGITUDE" in col:
        return "Long"
    elif col.startswith("TIME "):
        return "Time"
    elif col.startswith("DATE "):
        return "Date"
    else:
        return col.replace(" ", "_")


def clean_kor_measurements(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.rename(columns=rename_columns)
        .assign(
            Activity_Date_Time=lambda x: pd.to_datetime(x.Date + " " + x.Time),
            Activity_Date=lambda df_: pd.to_datetime(df_["Date"], format="%m/%d/%Y"),
        )
        .drop(columns=["Date", "Time"])
        .astype(
            {
                "SERIAL_NUMBER": "category",
                "SITE_NAME": "category",
            }
        )
    )


def parse_kor_measurements(file_path):
    """
    Parse Kor measurement export file into a pandas DataFrame.

    Parameters:
    -----------
    file_path : str
        Path to the Kor measurement export CSV file

    Returns:
    --------
    pandas.DataFrame
        Cleaned measurement data with appropriate columns and serial numbers
    """
    encodings = ["utf-16", "latin-1", "cp1252"]

    for encoding in encodings:
        try:
            with open(file_path, "r", encoding=encoding) as f:
                lines = f.readlines()
            break
        except UnicodeError:
            continue
    else:
        raise ValueError(f"Could not read file with any of the encodings: {encodings}")

    clean_lines = []
    current_serial = None
    headers = None

    for line in lines:
        line = line.strip()

        if not line:
            continue

        if line.startswith(("MEAN VALUE:", "STANDARD DEVIATION:")):
            continue

        if line.startswith("SENSOR SERIAL NUMBER:"):
            fields = line.split(",")
            if len(fields) >= 6:  # Ensure we have enough fields
                current_serial = fields[5].strip()  # 6th column (0-based index 5)
            continue

        # Capture headers
        if "TIME (HH:MM:SS)" in line:
            if len(line.strip().split(",")) == 24:
                headers = line.strip()
            continue

        # Process data lines (they should contain commas and not start with special markers)
        if (
            "," in line
            and not line.startswith(("sep=", "Kor MEASUREMENT", "FILE CREATED:"))
            and current_serial is not None
        ):  # Only add lines if we have a serial number
            # Add serial number to data line
            data_fields = line.split(",")
            if len(data_fields) > 4:  # Ensure it's a data line
                clean_lines.append(f"{current_serial},{line}")

    if headers and clean_lines:
        # Add SERIAL_NUMBER to headers
        headers = f"SERIAL_NUMBER,{headers}"

        # Combine headers and data into a single string
        csv_data = io.StringIO(f"{headers}\n" + "\n".join(clean_lines))

        df = pd.read_csv(csv_data)

        return clean_kor_measurements(df)

    return pd.DataFrame()  # Return empty DataFrame if no valid data found


def map_kor_measurements(df: pd.DataFrame, title: str = "Kor Measurements"):
    fig = px.scatter_mapbox(
        df,
        lat="Lat",
        lon="Long",
        hover_data=[
            df.index,
            "SERIAL_NUMBER",
            "SITE_NAME",
            "DEPTH_M",
            "Activity_Date_Time",
            "TEMP_°C",
            "ODO_%_SAT",
            "ODO_MG/L",
            "TURBIDITY_FNU",
            "SAL_PSU",
            "PH",
        ],
        color="SERIAL_NUMBER",
        zoom=10,
        mapbox_style="carto-positron",
    )

    # Update layout for better visibility
    fig.update_layout(
        title=title,
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        height=600,
    )

    return fig
