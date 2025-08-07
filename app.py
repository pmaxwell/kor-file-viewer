import os
import tempfile

import streamlit as st

from main import map_kor_measurements, parse_kor_measurements

# Set page config
st.set_page_config(page_title="Kor File Viewer", page_icon="📊", layout="wide")

# Title and description
st.title("📊 Kor File Viewer")
st.markdown("Upload a Kor measurement CSV file to view and map the data.")

# File uploader
uploaded_file = st.file_uploader(
    "Choose a CSV file", type=["csv"], help="Upload a Kor measurement export CSV file"
)

if uploaded_file is not None:
    try:
        # Create a temporary file to save the uploaded content
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name

        # Parse the file using the existing function
        with st.spinner("Parsing Kor measurements..."):
            df = parse_kor_measurements(tmp_file_path)

        # Clean up the temporary file
        os.unlink(tmp_file_path)

        if not df.empty:
            st.success(f"✅ Successfully parsed {len(df)} measurements!")

            # Date filtering section
            st.subheader("📅 Filter by Date")

            # Get date range from data
            if "Activity_Date_Time" in df.columns:
                min_date = df["Activity_Date_Time"].min()
                max_date = df["Activity_Date_Time"].max()

                # Filter type selection
                filter_type = st.radio(
                    "Choose filter type:",
                    ["No Filter", "Single Date", "Date Range"],
                    horizontal=True,
                )

                filtered_df = df.copy()

                if filter_type == "Single Date":
                    selected_date = st.date_input(
                        "Select a date:",
                        value=min_date.date(),
                        min_value=min_date.date(),
                        max_value=max_date.date(),
                        format="MM/DD/YYYY",
                    )

                    if selected_date:
                        # Filter for the selected date
                        filtered_df = df[
                            df["Activity_Date_Time"].dt.date == selected_date
                        ]

                elif filter_type == "Date Range":
                    col1, col2 = st.columns(2)

                    with col1:
                        start_date = st.date_input(
                            "Start date:",
                            value=min_date.date(),
                            min_value=min_date.date(),
                            max_value=max_date.date(),
                            format="MM/DD/YYYY",
                        )

                    with col2:
                        end_date = st.date_input(
                            "End date:",
                            value=max_date.date(),
                            min_value=min_date.date(),
                            max_value=max_date.date(),
                            format="MM/DD/YYYY",
                        )

                    if start_date and end_date and start_date <= end_date:
                        # Filter for the date range
                        filtered_df = df[
                            (df["Activity_Date_Time"].dt.date >= start_date)
                            & (df["Activity_Date_Time"].dt.date <= end_date)
                        ]
                    elif start_date and end_date and start_date > end_date:
                        st.error("⚠️ Start date must be before or equal to end date.")
                        filtered_df = df  # Show all data if invalid range

                # Show filter summary
                if filter_type != "No Filter":
                    st.info(
                        f"📊 Showing {len(filtered_df)} measurements out of {len(df)} total"
                    )

                    if len(filtered_df) == 0:
                        st.warning("⚠️ No measurements found for the selected date(s).")
                        filtered_df = df  # Show all data if no results
            else:
                st.warning("⚠️ No Activity_Date_Time column found in the data.")
                filtered_df = df

            # Display dataframe
            st.subheader("📋 Measurement Data")
            st.dataframe(filtered_df, use_container_width=True)

            # Display basic statistics
            st.subheader("📈 Data Summary")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total Measurements", len(filtered_df))

            with col2:
                st.metric("Unique Sensors", filtered_df["SERIAL_NUMBER"].nunique())

            with col3:
                st.metric("Unique Sites", filtered_df["SITE_NAME"].nunique())

            # Display the map
            st.subheader("🗺️ Interactive Map")

            # Check if we have location data
            if "Latitude" in filtered_df.columns and "Longitude" in filtered_df.columns:
                # Filter out rows without valid coordinates and coordinates with value 0
                df_with_coords = filtered_df.dropna(subset=["Latitude", "Longitude"])
                df_with_coords = df_with_coords[
                    (df_with_coords["Latitude"] != 0)
                    & (df_with_coords["Longitude"] != 0)
                ]

                if not df_with_coords.empty:
                    fig = map_kor_measurements(df_with_coords, "Kor Measurements Map")
                    st.plotly_chart(
                        fig,
                        use_container_width=True,
                        config={
                            "displayModeBar": True,
                            "displaylogo": False,
                            "modeBarButtonsToRemove": ["pan2d", "select2d", "lasso2d"],
                            "scrollZoom": True,
                        },
                    )

                    # Show coordinate statistics
                    st.info(
                        f"📍 {len(df_with_coords)} measurements have valid coordinates out of {len(filtered_df)} total measurements"
                    )
                else:
                    st.warning(
                        "⚠️ No measurements with valid coordinates found in the data."
                    )
            else:
                st.warning("⚠️ No latitude/longitude columns found in the parsed data.")

        else:
            st.error(
                "❌ No valid data found in the uploaded file. Please check the file format."
            )

    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        st.info(
            "💡 Make sure you're uploading a valid Kor measurement export CSV file."
        )

else:
    # Add some helpful information
    st.markdown("---")
    st.markdown("### 📋 Expected File Format")
    st.markdown("""
    Kor Measurement File Export csv exactly as it is exported from the Kor desktop software.
    """)
