import re
from datetime import datetime


# ============================================================
# HELPER: EXTRACT NUMBER
# ============================================================

def extract_number(pattern, text):
    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        try:
            return float(match.group(1))
        except (ValueError, TypeError):
            return None

    return None


# ============================================================
# HELPER: EXTRACT TEXT
# ============================================================

def extract_text(pattern, text):
    match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)

    if match:
        return match.group(1).strip()

    return None


# ============================================================
# MAIN WCR PARSER
# ============================================================

def parse_wcr(text):

    data = {}

    # --------------------------------------------------------
    # WELL ID
    # --------------------------------------------------------

    data["well_id"] = extract_text(
        r"Well\s+ID\b\s*[:\-]?\s*([A-Za-z0-9_\-]+)",
        text
    )

    # --------------------------------------------------------
    # WELL NAME
    # --------------------------------------------------------

    data["well_name"] = extract_text(
        r"Well\s+Name\s*[:\-]?\s*([A-Za-z0-9_\-]+)",
        text
    )

    # --------------------------------------------------------
    # OPERATOR
    # --------------------------------------------------------

    data["operator"] = extract_text(
        r"Operator\s*[:\-]?\s*(.+)",
        text
    )

    # --------------------------------------------------------
    # LOCATION
    # --------------------------------------------------------

    data["location"] = extract_text(
        r"Location\s*[:\-]?\s*(.+)",
        text
    )

   
    # --------------------------------------------------------
    # DRILLING DATE
    # --------------------------------------------------------

    drilling_date = extract_text(
        r"Drilling\s+Date\s*[:\-]?\s*([0-9A-Za-z\-]+)",
        text
    )

    if drilling_date:

        try:
            drilling_date = datetime.strptime(
                drilling_date,
                "%d-%b-%Y"
            ).strftime("%Y-%m-%d")

        except ValueError:
            pass

    data["drilling_date"] = drilling_date

    # --------------------------------------------------------
    # TOTAL DEPTH
    # --------------------------------------------------------

    data["total_depth"] = extract_number(
        r"total\s+(?:measured\s+)?depth\s+"
        r"(?:of|was|is)?\s*[:\-]?\s*([0-9.]+)\s*m",
        text
    )

    # --------------------------------------------------------
    # FORMATION
    # --------------------------------------------------------

    formation_match = re.search(
        r"formation\s+encountered\s+was\s+"
        r"([A-Za-z ]+?)(?:\.|,)",
        text,
        re.IGNORECASE
    )

    if formation_match:
        data["formation"] = formation_match.group(1).strip()
    else:
        data["formation"] = None

    # --------------------------------------------------------
    # ROP
    # --------------------------------------------------------

    data["rop"] = extract_number(
        r"(?:ROP|rate\s+of\s+penetration)"
        r"\s*(?:was|of|:)?\s*([0-9.]+)",
        text
    )

    # --------------------------------------------------------
    # WOB
    # --------------------------------------------------------

    data["wob"] = extract_number(
        r"(?:WOB|weight\s+on\s+bit)"
        r"\s*(?:was|of|:)?\s*([0-9.]+)",
        text
    )

    # --------------------------------------------------------
    # RPM
    # --------------------------------------------------------

    data["rpm"] = extract_number(
        r"(?:RPM|rotary\s+speed)"
        r"\s*(?:was|of|:)?\s*([0-9.]+)",
        text
    )

    # --------------------------------------------------------
    # TORQUE
    # --------------------------------------------------------

    data["torque"] = extract_number(
        r"torque\s*(?:was|of|:)?\s*([0-9.]+)",
        text
    )

    # --------------------------------------------------------
    # MUD WEIGHT
    # --------------------------------------------------------

    data["mud_weight"] = extract_number(
        r"mud\s+weight\s*(?:was|of|:)?\s*([0-9.]+)",
        text
    )

    # --------------------------------------------------------
    # RISK LEVEL
    # --------------------------------------------------------

    if re.search(
        r"moderate\s+risk",
        text,
        re.IGNORECASE
    ):

        data["risk_level"] = "Moderate"

    elif re.search(
        r"high\s+risk",
        text,
        re.IGNORECASE
    ):

        data["risk_level"] = "High"

    elif re.search(
        r"low\s+risk",
        text,
        re.IGNORECASE
    ):

        data["risk_level"] = "Low"

    else:

        data["risk_level"] = "Unknown"

    return data