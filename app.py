import streamlit as st
import pandas as pd
import tempfile
import os

from ocr import extract_text_from_pdf
from nlp_parser import parse_wcr
from database import insert_wcr_data, get_all_wcr_data
import ui


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="NWIS - Drilling Intelligence",
    page_icon="🛢️",
    layout="wide"
)


# ============================================================
# HEADER
# ============================================================

ui.inject_css()
ui.header()


# ============================================================
# SIDEBAR
# ============================================================

ui.sidebar_workflow()


# ============================================================
# SECTION 1 - UPLOAD WCR
# ============================================================

ui.section("📄 1. Upload WCR Report")

# ============================================================
# WCR INPUT OPTIONS
# ============================================================

col_upload, col_demo = st.columns(2)

with col_upload:

    uploaded_file = st.file_uploader(
        "Upload a Well Completion Report (PDF)",
        type=["pdf"]
    )


with col_demo:

    st.markdown("### 🚀 Quick Demo")

    demo_button = st.button(
        "🚀 Run Demo with Sample WCR",
        type="secondary"
    )


# ============================================================
# SELECT INPUT FILE
# ============================================================

file_name = None
file_bytes = None


# Normal user upload
if uploaded_file:

    file_name = uploaded_file.name
    file_bytes = uploaded_file.getvalue()

    st.success(
        f"File uploaded: {file_name}"
    )


# Demo sample from GitHub
elif demo_button:

    sample_path = "sample_WCR.pdf"

    if os.path.exists(sample_path):

        with open(
            sample_path,
            "rb"
        ) as f:

            file_bytes = f.read()

        file_name = "sample_WCR.pdf"

        st.success(
            "✅ Sample WCR loaded from the project"
        )

    else:

        st.error(
            "❌ sample_WCR.pdf was not found in the repository."
        )


# ============================================================
# PROCESS SELECTED FILE
# ============================================================

if file_bytes is not None:

    # --------------------------------------------------------
    # PROCESS BUTTON
    # --------------------------------------------------------

    if st.button(
        "🚀 Process WCR Report",
        type="primary"
    ):

        # ----------------------------------------------------
        # SAVE PDF TEMPORARILY
        # ----------------------------------------------------

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as tmp:

            tmp.write(
                uploaded_file.read()
            )

            pdf_path = tmp.name


        # ----------------------------------------------------
        # PROCESSING
        # ----------------------------------------------------

        with st.status(
            "Processing WCR Report...",
            expanded=True
        ) as status:

            # =================================================
            # STEP 1 - PDF / OCR
            # =================================================

            st.write(
                "📄 Reading WCR PDF..."
            )

            try:

                text = extract_text_from_pdf(
                    pdf_path
                )

                st.write(
                    "✅ PDF text extraction completed"
                )

            except Exception as e:

                st.error(
                    f"PDF/OCR processing failed: {e}"
                )

                status.update(
                    label="PDF processing failed",
                    state="error"
                )

                os.remove(pdf_path)

                st.stop()


            # =================================================
            # STEP 2 - NLP
            # =================================================

            st.write(
                "🧠 Extracting structured information..."
            )

            try:

                data = parse_wcr(
                    text
                )

                st.write(
                    "✅ NLP extraction completed"
                )

            except Exception as e:

                st.error(
                    f"NLP extraction failed: {e}"
                )

                status.update(
                    label="NLP processing failed",
                    state="error"
                )

                os.remove(pdf_path)

                st.stop()


            # =================================================
            # CLEAN DATA
            # =================================================

            clean_data = {
                key: value
                for key, value in data.items()
                if value is not None
            }


            # =================================================
            # STEP 3 - DATABASE
            # =================================================

            st.write(
                "🗄️ Storing structured data in Supabase..."
            )

            try:

                insert_wcr_data(
                    clean_data
                )

                st.session_state["wcr_processed"] = True

                st.write(
                    "✅ Database updated successfully"
                )

                status.update(
                    label="WCR processing completed successfully!",
                    state="complete"
                )

            except Exception as e:

                status.update(
                    label="Database insertion failed",
                    state="error"
                )

                st.error(
                    "❌ Database insertion failed"
                )

                st.code(
                    str(e)
                )


        # ----------------------------------------------------
        # REMOVE TEMPORARY PDF
        # ----------------------------------------------------

        try:

            os.remove(
                pdf_path
            )

        except:

            pass


        # ====================================================
        # SECTION 2 - EXTRACTED TEXT
        # ====================================================

        ui.section("🔍 2. Extracted Report Text")

        with st.expander(
            "View extracted WCR text"
        ):

            st.text(
                text
            )


        # ====================================================
        # SECTION 3 - NLP STRUCTURED DATA
        # ====================================================

        ui.section(
            "🧠 3. NLP Extracted Structured Data"
        )

        display_data = pd.DataFrame(
            list(data.items()),
            columns=[
                "Field",
                "Extracted Value"
            ]
        )

        # Convert mixed values to text
        display_data["Extracted Value"] = (
            display_data["Extracted Value"].astype(str)
        )

        st.dataframe(
            display_data,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# SECTION 4 - SUPABASE DATABASE
# ============================================================

ui.section(
    "🗄️ 4. Supabase WCR Database"
)

try:

    db_data = get_all_wcr_data()

    if db_data:

        db_df = pd.DataFrame(
            db_data
        )

        # ----------------------------------------------------
        # KPI CARDS
        # ----------------------------------------------------

        total_records = len(db_df)

        total_wells = (
            db_df["well_id"].nunique()
            if "well_id" in db_df.columns
            else total_records
        )

        avg_depth = 0

        if "total_depth" in db_df.columns:

            avg_depth = pd.to_numeric(
                db_df["total_depth"],
                errors="coerce"
            ).mean()

        avg_rop = 0

        if "rop" in db_df.columns:

            avg_rop = pd.to_numeric(
                db_df["rop"],
                errors="coerce"
            ).mean()


        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "📄 WCR Records",
                total_records
            )

        with col2:

            st.metric(
                "🛢️ Unique Wells",
                total_wells
            )

        with col3:

            st.metric(
                "📏 Avg Depth",
                f"{avg_depth:.1f}"
                if pd.notna(avg_depth)
                else "N/A"
            )

        with col4:

            st.metric(
                "⚙️ Avg ROP",
                f"{avg_rop:.1f}"
                if pd.notna(avg_rop)
                else "N/A"
            )


        # ----------------------------------------------------
        # DATABASE TABLE
        # ----------------------------------------------------

        st.markdown(
            "### 📊 Stored WCR Records"
        )

        st.dataframe(
            db_df,
            use_container_width=True,
            hide_index=True
        )


        # ----------------------------------------------------
        # DRILLING PARAMETERS
        # ----------------------------------------------------

        st.markdown(
            "### ⚙️ Drilling Parameters"
        )

        parameter_columns = [
            "well_id",
            "well_name",
            "total_depth",
            "formation",
            "rop",
            "wob",
            "rpm",
            "torque",
            "mud_weight",
            "risk_level"
        ]

        available_columns = [
            column
            for column in parameter_columns
            if column in db_df.columns
        ]

        if available_columns:

            st.dataframe(
                db_df[available_columns],
                use_container_width=True,
                hide_index=True
            )


    else:

        st.info(
            "No WCR records found in Supabase."
        )


except Exception as e:

    st.error(
        f"Unable to read Supabase records: {e}"
    )


# ============================================================
# SECTION 5 - DEMO WORKFLOW
# ============================================================

ui.section(
    "🔄 5. NWIS Processing Pipeline"
)

pipeline = """
WCR / DDR Report
        ↓
PDF Text Extraction / OCR
        ↓
NLP Information Extraction
        ↓
Structured Drilling Data
        ↓
Supabase PostgreSQL
        ↓
NWIS Intelligence Dashboard
        ↓
Planned: Similar Wells • eRTMAC • Risk Prediction • GIS
"""

st.code(
    pipeline,
    language="text"
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

ui.footer()
