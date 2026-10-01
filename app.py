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
# SIDEBAR - PROJECT WORKFLOW
# ============================================================

ui.sidebar_workflow()


# ============================================================
# SECTION 1 - UPLOAD WCR
# ============================================================

ui.section("📄 1. Upload WCR Report")

uploaded_file = st.file_uploader(
    "Upload a Well Completion Report (PDF)",
    type=["pdf"]
)


if uploaded_file:

    st.success(
        f"File uploaded: {uploaded_file.name}"
    )

    # --------------------------------------------------------
    # PROCESS BUTTON
    # --------------------------------------------------------

    if st.button(
        "🚀 Process WCR Report",
        type="primary"
    ):

        # ----------------------------------------------------
        # SAVE UPLOADED PDF TEMPORARILY
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

            # ------------------------------------------------
            # STEP 1 - PDF / OCR
            # ------------------------------------------------

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


            # ------------------------------------------------
            # STEP 2 - NLP
            # ------------------------------------------------

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


            # ------------------------------------------------
            # CLEAN DATA
            # ------------------------------------------------

            clean_data = {
                key: value
                for key, value in data.items()
                if value is not None
            }


            # ------------------------------------------------
            # STEP 3 - DATABASE
            # ------------------------------------------------

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
        # SECTION 3 - STRUCTURED DATA
        # ====================================================

        ui.section("🧠 3. NLP Extracted Structured Data")

        display_data = pd.DataFrame(
            list(data.items()),
            columns=[
                "Field",
                "Extracted Value"
            ]
        )

        st.dataframe(
            display_data,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# SECTION 4 - SUPABASE DATABASE
# ============================================================

if st.session_state.get("wcr_processed"):

    st.divider()

    ui.section("🗄️ 4. Structured Database – Supabase")

    try:

        records = get_all_wcr_data()

        if records:

            df = pd.DataFrame(
                records
            )

            st.success(
                f"🟢 Supabase connected — {len(df)} record(s) stored"
            )

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "Supabase connected, but no records are stored yet."
            )

    except Exception as e:

        st.error(
            "❌ Database connection error"
        )

        st.code(
            str(e)
        )


    # ============================================================
    # SECTION 5 - DATABASE STATISTICS
    # ============================================================

    st.divider()

    ui.section("📊 5. Database Overview")

    try:

        records = get_all_wcr_data()

        if records:

            df = pd.DataFrame(
                records
            )

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.metric(
                    "Total Records",
                    len(df)
                )

            with col2:

                if "well_id" in df.columns:

                    st.metric(
                        "Unique Wells",
                        df["well_id"].nunique()
                    )

            with col3:

                if "formation" in df.columns:

                    st.metric(
                        "Formations",
                        df["formation"].nunique()
                    )

            with col4:

                if "risk_level" in df.columns:

                    st.metric(
                        "Risk Categories",
                        df["risk_level"].nunique()
                    )

    except Exception:

        pass

else:

    st.divider()

    st.info(
        "Process a WCR report above to see the stored database records here."
    )


# ============================================================
# DEPTH EXPLORER (simulated preview of planned modules)
# ============================================================

st.divider()

ui.section("Depth risk explorer", "Preview of the planned risk engine. Values here are simulated, not model output.")

ui.explorer_component()


# ============================================================
# SECTION 6 - NWIS END-TO-END WORKFLOW
# ============================================================

st.divider()

ui.section("🔄 6. NWIS End-to-End Workflow")

workflow = """
WCR / DDR Documents
        ↓
PDF Processing
        ↓
OCR / Text Extraction
        ↓
NLP & Information Extraction
        ↓
Structured Data
        ↓
Supabase PostgreSQL
        ↓
Similar Well Identification
        ↓
Real-Time eRTMAC Data
        ↓
Feature Alignment
        ↓
Risk Prediction
        ↓
SHAP Explainability
        ↓
Alerts & Recommendations
        ↓
GIS-Based NWIS Dashboard
"""

ui.pipeline_component()


# ============================================================
# SECTION 7 - DEMO STATUS
# ============================================================

st.divider()

ui.section("🚀 Prototype Status")

status_data = {
    "Component": [
        "WCR PDF Upload",
        "PDF Text Extraction",
        "OCR Fallback",
        "NLP Field Extraction",
        "Structured Data Generation",
        "Supabase Database",
        "Dashboard Visualization",
        "Similar Well Engine",
        "Real-Time eRTMAC Integration",
        "Risk Prediction",
        "GIS Dashboard"
    ],
    "Status": [
        "✅ Working",
        "✅ Working",
        "✅ Working",
        "✅ Working",
        "✅ Working",
        "✅ Connected",
        "✅ Working",
        "🔄 Planned",
        "🔄 Planned",
        "🔄 Planned",
        "🔄 Planned"
    ]
}

status_df = pd.DataFrame(
    status_data
)

st.dataframe(
    status_df,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

ui.footer()