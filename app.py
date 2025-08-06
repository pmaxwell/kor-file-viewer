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

            # Display dataframe
            st.subheader("📋 Measurement Data")
            st.dataframe(df, use_container_width=True)

            # Display basic statistics
            st.subheader("📈 Data Summary")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total Measurements", len(df))

            with col2:
                st.metric("Unique Sensors", df["SERIAL_NUMBER"].nunique())

            with col3:
                st.metric("Unique Sites", df["SITE_NAME"].nunique())

            # Display the map
            st.subheader("🗺️ Interactive Map")

            # Check if we have location data
            if "Lat" in df.columns and "Long" in df.columns:
                # Filter out rows without valid coordinates and coordinates with value 0
                df_with_coords = df.dropna(subset=["Lat", "Long"])
                df_with_coords = df_with_coords[
                    (df_with_coords["Lat"] != 0) & (df_with_coords["Long"] != 0)
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
                        f"📍 {len(df_with_coords)} measurements have valid coordinates out of {len(df)} total measurements"
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
    st.info("👆 Please upload a CSV file to get started.")

    # Add some helpful information
    st.markdown("---")
    st.markdown("### 📋 Expected File Format")
    st.markdown("""
    Kor Measurement File Export csv exactly as it is exported from the Kor desktop software.
    """)
