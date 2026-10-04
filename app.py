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
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# NWIS UI (theme, navbar, hero, sidebar)
# ============================================================

ui.inject_css()
ui.header()
ui.sidebar_workflow()


# ============================================================
# SECTION 1 - WCR INPUT
# ============================================================

ui.section("📄 1. Upload WCR Report")

ui.html("""
    <div style="
        color:#486581;
        font-size:15px;
        margin-bottom:14px;
    ">
        Upload a Well Completion Report or run the built-in
        demonstration using the sample WCR.
    </div>
    """)


# ============================================================
# INPUT OPTIONS
# ============================================================

col_upload, col_demo = st.columns(
    [1.4, 1],
    gap="large"
)


with col_upload:

    st.markdown(
        "### 📄 Upload your WCR",
    )

    uploaded_file = st.file_uploader(
        "Upload a Well Completion Report (PDF)",
        type=["pdf"],
        key="wcr_uploader"
    )


with col_demo:

    st.markdown(
        "### 🚀 Quick Demo"
    )

    ui.html("""
        <div style="
            color:#486581;
            font-size:14px;
            margin-bottom:10px;
        ">
            No file required. Use the sample WCR
            bundled with the project.
        </div>
        """)

    demo_button = st.button(
        "🚀 Run Demo with Sample WCR",
        type="secondary",
        use_container_width=True
    )


# ============================================================
# SELECT INPUT
# ============================================================

file_name = None
file_bytes = None


# ------------------------------------------------------------
# NORMAL UPLOAD
# ------------------------------------------------------------

if uploaded_file:

    file_name = uploaded_file.name

    file_bytes = uploaded_file.getvalue()

    st.success(
        f"✅ File uploaded: {file_name}"
    )


# ------------------------------------------------------------
# SAMPLE DEMO
# ------------------------------------------------------------

elif demo_button:

    sample_path = os.path.join(
        os.path.dirname(__file__),
        "sample_WCR.pdf"
    )

    if os.path.exists(sample_path):

        with open(
            sample_path,
            "rb"
        ) as f:

            file_bytes = f.read()

        file_name = "sample_WCR.pdf"

        st.success(
            "🚀 Sample WCR loaded successfully."
        )

    else:

        st.error(
            "❌ sample_WCR.pdf was not found in the project."
        )


# ============================================================
# PROCESS WCR
# ============================================================

if file_bytes is not None:

    st.markdown(
        "### ⚙️ Processing Pipeline"
    )

    ui.html("""
        <div style="
            display:flex;
            align-items:center;
            justify-content:space-between;
            gap:8px;
            padding:18px;
            background:rgba(255,255,255,0.9);
            border-radius:14px;
            border:1px solid #D9E2EC;
            margin-bottom:20px;
            overflow-x:auto;
        ">

            <div style="text-align:center;min-width:120px;">
                <div style="font-size:28px;">📄</div>
                <b>WCR / DDR</b>
                <div style="font-size:12px;color:#627D98;">
                    Report
                </div>
            </div>

            <div style="font-size:22px;color:#F15A29;">→</div>

            <div style="text-align:center;min-width:120px;">
                <div style="font-size:28px;">🔍</div>
                <b>OCR</b>
                <div style="font-size:12px;color:#627D98;">
                    Extraction
                </div>
            </div>

            <div style="font-size:22px;color:#F15A29;">→</div>

            <div style="text-align:center;min-width:120px;">
                <div style="font-size:28px;">🧠</div>
                <b>NLP</b>
                <div style="font-size:12px;color:#627D98;">
                    Information
                </div>
            </div>

            <div style="font-size:22px;color:#F15A29;">→</div>

            <div style="text-align:center;min-width:120px;">
                <div style="font-size:28px;">🗃️</div>
                <b>Structured DB</b>
                <div style="font-size:12px;color:#627D98;">
                    PostgreSQL
                </div>
            </div>

            <div style="font-size:22px;color:#F15A29;">→</div>

            <div style="text-align:center;min-width:120px;">
                <div style="font-size:28px;">📊</div>
                <b>Intelligence</b>
                <div style="font-size:12px;color:#627D98;">
                    Dashboard
                </div>
            </div>

        </div>
        """)


    # ========================================================
    # TEMPORARY PDF
    # ========================================================

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    ) as tmp:

        tmp.write(
            file_bytes
        )

        pdf_path = tmp.name


    text = None
    data = None


    # ========================================================
    # PROCESSING STATUS
    # ========================================================

    with st.status(
        "Processing WCR Report...",
        expanded=True
    ) as status:

        # ----------------------------------------------------
        # STEP 1 - PDF / OCR
        # ----------------------------------------------------

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

            try:
                os.remove(pdf_path)
            except:
                pass

            st.stop()


        # ----------------------------------------------------
        # STEP 2 - NLP
        # ----------------------------------------------------

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

            try:
                os.remove(pdf_path)
            except:
                pass

            st.stop()


        # ----------------------------------------------------
        # CLEAN DATA
        # ----------------------------------------------------

        clean_data = {
            key: value
            for key, value in data.items()
            if value is not None
        }


        # ----------------------------------------------------
        # STEP 3 - SUPABASE
        # ----------------------------------------------------

        st.write(
            "🗄️ Storing structured data in Supabase..."
        )

        try:

            insert_wcr_data(
                clean_data
            )

            st.session_state[
                "wcr_processed"
            ] = True

            st.write(
                "✅ Supabase database updated successfully"
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


    # ========================================================
    # REMOVE TEMPORARY FILE
    # ========================================================

    try:

        os.remove(
            pdf_path
        )

    except:

        pass


    # ========================================================
    # SECTION 2 - EXTRACTED TEXT
    # ========================================================

    ui.section(
        "🔍 2. Extracted Report Text"
    )

    with st.expander(
        "View extracted WCR text"
    ):

        if text:

            st.text(
                text
            )


    # ========================================================
    # SECTION 3 - NLP STRUCTURED DATA
    # ========================================================

    ui.section(
        "🧠 3. NLP Extracted Structured Data"
    )

    if data:

        display_data = pd.DataFrame(
            list(data.items()),
            columns=[
                "Field",
                "Extracted Value"
            ]
        )

        display_data[
            "Extracted Value"
        ] = (
            display_data[
                "Extracted Value"
            ].astype(str)
        )

        st.dataframe(
            display_data,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# SECTION 4 - SUPABASE DATABASE
# (shown only after a WCR has been processed and stored)
# ============================================================

if st.session_state.get("wcr_processed"):

    ui.section(
        "🗄️ 4. Supabase WCR Database"
    )

    try:

        db_data = get_all_wcr_data()

        if db_data:

            db_df = pd.DataFrame(
                db_data
            )


            # ================================================
            # KPI CARDS
            # ================================================

            total_records = len(
                db_df
            )


            if "well_id" in db_df.columns:

                total_wells = db_df[
                    "well_id"
                ].nunique()

            else:

                total_wells = total_records


            if "total_depth" in db_df.columns:

                depth_values = pd.to_numeric(
                    db_df["total_depth"],
                    errors="coerce"
                )

                avg_depth = depth_values.mean()

            else:

                avg_depth = None


            if "rop" in db_df.columns:

                rop_values = pd.to_numeric(
                    db_df["rop"],
                    errors="coerce"
                )

                avg_rop = rop_values.mean()

            else:

                avg_rop = None


            col1, col2, col3, col4 = st.columns(
                4,
                gap="medium"
            )


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


            # ================================================
            # DATABASE RECORDS
            # ================================================

            st.markdown(
                "### 📊 Stored WCR Records"
            )

            st.dataframe(
                db_df,
                use_container_width=True,
                hide_index=True
            )


            # ================================================
            # DRILLING PARAMETERS
            # ================================================

            st.markdown(
                "### ⚙️ Drilling Parameters"
            )

            parameter_columns = [
                "well_id",
                "well_name",
                "operator",
                "location",
                "drilling_date",
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
                    db_df[
                        available_columns
                    ],
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

else:

    st.info(
        "Process a WCR report above to see the stored database records here."
    )


# ============================================================
# SECTION 5 - CURRENT + PLANNED INTELLIGENCE
# ============================================================

ui.section(
    "🧠 5. NWIS Intelligence Modules"
)


module_col1, module_col2 = st.columns(
    2,
    gap="large"
)


with module_col1:

    ui.html("""
        <div style="
            background:#FFFFFF;
            padding:22px;
            border-radius:16px;
            border-left:5px solid #0F9EA8;
            margin-bottom:14px;
        ">
            <h3 style="color:#102A43;margin-top:0;">
                ✅ Current Prototype
            </h3>

            <p style="color:#486581;">
                <b>WCR / DDR Processing</b><br>
                Automated PDF text extraction and OCR.
            </p>

            <p style="color:#486581;">
                <b>NLP Information Extraction</b><br>
                Converts report content into structured
                drilling parameters.
            </p>

            <p style="color:#486581;">
                <b>Supabase PostgreSQL</b><br>
                Stores structured well information for
                downstream intelligence.
            </p>

            <p style="color:#486581;">
                <b>Dashboard Analytics</b><br>
                Displays well records and drilling KPIs.
            </p>
        </div>
        """)


with module_col2:

    ui.html("""
        <div style="
            background:#FFFFFF;
            padding:22px;
            border-radius:16px;
            border-left:5px solid #F15A29;
            margin-bottom:14px;
        ">
            <h3 style="color:#102A43;margin-top:0;">
                🔮 Planned Intelligence
            </h3>

            <p style="color:#486581;">
                <b>○ Similar Well Identification</b><br>
                Identify relevant offset wells using
                geological and spatial similarity.
            </p>

            <p style="color:#486581;">
                <b>○ Real-time eRTMAC Integration</b><br>
                Incorporate live drilling parameters
                into the intelligence layer.
            </p>

            <p style="color:#486581;">
                <b>○ Risk Prediction + SHAP</b><br>
                Predict drilling risks and explain
                model decisions.
            </p>

            <p style="color:#486581;">
                <b>○ Recommendation Engine</b><br>
                Generate actionable drilling recommendations.
            </p>

            <p style="color:#486581;">
                <b>○ GIS Dashboard</b><br>
                Provide spatial well intelligence and
                map-based decision support.
            </p>
        </div>
        """)


# ============================================================
# SECTION 6 - DEPTH RISK EXPLORER
# (simulated preview of the planned risk engine)
# ============================================================

ui.section(
    "🎯 6. Depth Risk Explorer",
    "Preview of the planned risk engine. Values here are simulated, not model output."
)

ui.explorer_component()


# ============================================================
# SECTION 7 - END-TO-END ARCHITECTURE
# ============================================================

ui.section(
    "🔄 7. End-to-End NWIS Architecture"
)

ui.pipeline_component()


# ============================================================
# SECTION 8 - PROTOTYPE STATUS
# ============================================================

ui.section(
    "📌 8. Prototype Status"
)

status_col1, status_col2, status_col3 = st.columns(
    3,
    gap="medium"
)


with status_col1:

    st.success(
        "✅ WCR Processing"
    )

    st.caption(
        "PDF → OCR → NLP"
    )


with status_col2:

    st.success(
        "✅ Supabase Storage"
    )

    st.caption(
        "Structured PostgreSQL database"
    )


with status_col3:

    st.info(
        "🔮 Intelligence Layer"
    )

    st.caption(
        "Similar wells, eRTMAC, risk, GIS"
    )


# ============================================================
# FOOTER
# ============================================================

ui.footer()
