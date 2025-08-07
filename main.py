import io

import pandas as pd
import plotly.express as px


def rename_columns(col):
    if "LATITUDE" in col:
        return "Latitude"
    elif "LONGITUDE" in col:
        return "Longitude"
    elif col.startswith("TIME "):
        return "Time"
    elif col.startswith("DATE "):
        return "Date"
    else:
        return col.replace(" ", "_")


def clean_kor_measurements(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.rename(columns=rename_columns)
        .query("SERIAL_NUMBER != 'TBD'")
        .assign(
            Activity_Date_Time=lambda x: pd.to_datetime(x.Date + " " + x.Time),
            # Activity_Date=lambda df_: pd.to_datetime(df_["Date"], format="%m/%d/%Y"),
        )
        .drop(columns=["Date", "Time"])
        .astype(
            {
                "SERIAL_NUMBER": "category",
            }
        )
        .assign(SITE_NAME=lambda x: x["SITE_NAME"].astype("string"))
        .pipe(
            lambda df_: df_.reindex(
                columns=[
                    "Activity_Date_Time",
                    *[
                        col
                        for col in df_.columns
                        if col not in ["Activity_Date_Time", "FILE_NAME", "SITE_NAME"]
                    ],
                    "FILE_NAME",
                    "SITE_NAME",
                ]
            )
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

    all_data_blocks = []
    current_block = {"serial": None, "headers": None, "data_lines": []}

    for line in lines:
        line = line.strip()

        if not line:
            continue

        if line.startswith(("MEAN VALUE:", "STANDARD DEVIATION:")):
            continue

        # Start a new block when we encounter a new serial number line
        if line.startswith("SENSOR SERIAL NUMBER:"):
            # Save the previous block if it has data
            if current_block["headers"] and current_block["data_lines"]:
                all_data_blocks.append(current_block)

            # Start a new block
            current_block = {"serial": None, "headers": None, "data_lines": []}

            # Parse the serial number
            fields = line.split(",")
            # Look for the first non-empty serial number starting from index 4
            for i in range(4, min(7, len(fields))):
                if i < len(fields) and fields[i].strip():
                    current_block["serial"] = fields[i].strip()
                    break
            continue

        # Capture headers for current block
        if "TIME (HH:MM:SS)" in line:
            current_block["headers"] = line.strip()
            continue

        # Process data lines for current block
        if (
            "," in line
            and not line.startswith(("sep=", "Kor MEASUREMENT", "FILE CREATED:"))
            and current_block["serial"] is not None
        ):
            data_fields = line.split(",")
            if len(data_fields) > 9:  # Ensure it's a data line
                current_block["data_lines"].append(line)

    # Don't forget the last block
    if current_block["headers"] and current_block["data_lines"]:
        all_data_blocks.append(current_block)

    # Process each block separately and create DataFrames
    dataframes = []

    for block in all_data_blocks:
        if block["headers"] and block["data_lines"]:
            # Create CSV data for this block
            block_csv_data = io.StringIO()

            # Add headers with serial number column
            headers_with_serial = f"SERIAL_NUMBER,{block['headers']}"
            block_csv_data.write(f"{headers_with_serial}\n")

            # Add data lines with serial number
            for data_line in block["data_lines"]:
                block_csv_data.write(f"{block['serial']},{data_line}\n")

            # Reset position for reading
            block_csv_data.seek(0)

            # Read this block into a DataFrame
            try:
                block_df = pd.read_csv(block_csv_data)
                dataframes.append(block_df)
            except Exception as e:
                print(
                    f"Warning: Could not parse block with serial {block['serial']}: {e}"
                )
                continue

    if dataframes:
        # Concatenate all DataFrames
        combined_df = pd.concat(dataframes, ignore_index=True)
        return clean_kor_measurements(combined_df)

    return pd.DataFrame()  # Return empty DataFrame if no valid data found


def map_kor_measurements(df: pd.DataFrame, title: str = "Kor Measurements"):
    fig = px.scatter_mapbox(
        df,
        lat="Latitude",
        lon="Longitude",
        hover_data=[
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
