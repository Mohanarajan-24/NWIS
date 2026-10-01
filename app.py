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

# Convert mixed values to text for safe Streamlit display
display_data["Extracted Value"] = display_data["Extracted Value"].astype(str)

st.dataframe(
    display_data,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

ui.footer()
