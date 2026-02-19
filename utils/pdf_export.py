"""
PDF Export Utility - Generates PDF reports from Zoho CRM record sets.
Uses fpdf2 for landscape A4 tables with module-specific column definitions.
"""

import os
import tempfile
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from fpdf import FPDF

logger = logging.getLogger(__name__)

# Module-specific column definitions: (header, zoho_field, width_pct)
MODULE_COLUMNS = {
    "Leads": [
        ("Name", "_full_name", 18),
        ("Company", "Company", 16),
        ("Email", "Email", 20),
        ("Phone", "Phone", 14),
        ("Status", "Lead_Status", 10),
        ("Source", "Lead_Source", 10),
        ("Created", "Created_Time", 12),
    ],
    "Contacts": [
        ("Name", "_full_name", 18),
        ("Email", "Email", 22),
        ("Phone", "Phone", 16),
        ("Account", "_account_name", 18),
        ("Created", "Created_Time", 12),
        ("ID", "id", 14),
    ],
    "Accounts": [
        ("Account Name", "Account_Name", 22),
        ("Phone", "Phone", 16),
        ("Website", "Website", 20),
        ("Industry", "Industry", 16),
        ("Created", "Created_Time", 12),
        ("ID", "id", 14),
    ],
    "Deals": [
        ("Deal Name", "Deal_Name", 22),
        ("Stage", "Stage", 16),
        ("Amount", "_amount_fmt", 14),
        ("Closing Date", "Closing_Date", 14),
        ("Account", "_account_name", 16),
        ("Created", "Created_Time", 12),
        ("ID", "id", 6),
    ],
    "Products": [
        ("Product Name", "Product_Name", 26),
        ("Unit Price", "_price_fmt", 16),
        ("Product Code", "Product_Code", 16),
        ("Description", "Description", 26),
        ("ID", "id", 16),
    ],
    "Vendors": [
        ("Vendor Name", "Vendor_Name", 24),
        ("Email", "Email", 24),
        ("Phone", "Phone", 18),
        ("Website", "Website", 20),
        ("ID", "id", 14),
    ],
    "Quotes": [
        ("Subject", "Subject", 28),
        ("Stage", "Quote_Stage", 18),
        ("Deal", "Deal_Name", 18),
        ("Account", "Account_Name", 18),
        ("ID", "id", 18),
    ],
    "Sales_Orders": [
        ("Subject", "Subject", 30),
        ("Status", "Status", 18),
        ("Account", "Account_Name", 20),
        ("Grand Total", "_grand_total_fmt", 16),
        ("ID", "id", 16),
    ],
    "Purchase_Orders": [
        ("Subject", "Subject", 30),
        ("Status", "Status", 18),
        ("Vendor", "Vendor_Name", 20),
        ("Grand Total", "_grand_total_fmt", 16),
        ("ID", "id", 16),
    ],
    "Invoices": [
        ("Subject", "Subject", 30),
        ("Status", "Status", 18),
        ("Account", "Account_Name", 20),
        ("Grand Total", "_grand_total_fmt", 16),
        ("ID", "id", 16),
    ],
    "Tasks": [
        ("Subject", "Subject", 26),
        ("Status", "Status", 14),
        ("Priority", "Priority", 12),
        ("Due Date", "Due_Date", 14),
        ("Related To", "_what_id_name", 18),
        ("ID", "id", 16),
    ],
}

# Fallback columns for unknown modules
DEFAULT_COLUMNS = [
    ("Name/Subject", "_display_name", 30),
    ("Created", "Created_Time", 20),
    ("Modified", "Modified_Time", 20),
    ("ID", "id", 30),
]


def _sanitize_text(text: str) -> str:
    """Replace Unicode characters unsupported by Helvetica with ASCII equivalents."""
    replacements = {
        "\u2018": "'", "\u2019": "'",   # smart single quotes
        "\u201C": '"', "\u201D": '"',   # smart double quotes
        "\u2013": "-", "\u2014": "-",   # en-dash, em-dash
        "\u2026": "...",                 # ellipsis
        "\u00A0": " ",                   # non-breaking space
        "\u2022": "-",                   # bullet
        "\u00B0": "o",                   # degree sign
        "\u00E9": "e", "\u00E8": "e",   # accented e
        "\u00F1": "n",                   # ñ
        "\u00E1": "a", "\u00E0": "a",   # accented a
        "\u00ED": "i", "\u00EC": "i",   # accented i
        "\u00F3": "o", "\u00F2": "o",   # accented o
        "\u00FA": "u", "\u00F9": "u",   # accented u
    }
    for orig, repl in replacements.items():
        text = text.replace(orig, repl)
    # Strip any remaining non-latin1 characters
    return text.encode("latin-1", errors="replace").decode("latin-1")


def _extract_field(record: Dict[str, Any], field: str) -> str:
    """Extract a field value from a record, handling virtual fields."""
    if field == "_full_name":
        first = record.get("First_Name", "") or ""
        last = record.get("Last_Name", "") or ""
        return f"{first} {last}".strip() or "N/A"

    if field == "_account_name":
        acct = record.get("Account_Name")
        if isinstance(acct, dict):
            return acct.get("name", "N/A")
        return str(acct) if acct else "N/A"

    if field == "_amount_fmt":
        amount = record.get("Amount")
        if amount is not None:
            try:
                return f"${float(amount):,.2f}"
            except (ValueError, TypeError):
                return str(amount)
        return "N/A"

    if field == "_price_fmt":
        price = record.get("Unit_Price")
        if price is not None:
            try:
                return f"${float(price):,.2f}"
            except (ValueError, TypeError):
                return str(price)
        return "N/A"

    if field == "_grand_total_fmt":
        total = record.get("Grand_Total")
        if total is not None:
            try:
                return f"${float(total):,.2f}"
            except (ValueError, TypeError):
                return str(total)
        return "N/A"

    if field == "_what_id_name":
        what_id = record.get("What_Id")
        if isinstance(what_id, dict):
            return what_id.get("name", what_id.get("id", "N/A"))
        return str(what_id) if what_id else "N/A"

    if field == "_display_name":
        for key in ("Subject", "Name", "Full_Name", "Product_Name",
                     "Account_Name", "Deal_Name", "Vendor_Name"):
            val = record.get(key)
            if val:
                return str(val) if not isinstance(val, dict) else val.get("name", str(val))
        first = record.get("First_Name", "") or ""
        last = record.get("Last_Name", "") or ""
        if first or last:
            return f"{first} {last}".strip()
        return "N/A"

    val = record.get(field)
    if val is None:
        return "N/A"
    if isinstance(val, dict):
        return val.get("name", str(val))
    # Truncate Created_Time to date only
    if field == "Created_Time" and isinstance(val, str) and "T" in val:
        return val.split("T")[0]
    return str(val)


def generate_crm_pdf(
    records: List[Dict[str, Any]],
    module: str,
    title: Optional[str] = None,
) -> str:
    """
    Generate a PDF table from CRM records.

    Args:
        records: List of Zoho CRM record dicts
        module: Module name (Leads, Contacts, etc.)
        title: Optional report title

    Returns:
        Path to the generated temporary PDF file
    """
    if not title:
        title = f"{module} Report"

    columns = MODULE_COLUMNS.get(module, DEFAULT_COLUMNS)

    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, _sanitize_text(title), new_x="LMARGIN", new_y="NEXT", align="C")

    # Subtitle with count and date
    pdf.set_font("Helvetica", "", 9)
    subtitle = f"{len(records)} records | Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    pdf.cell(0, 6, subtitle, new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(4)

    # Calculate column widths based on page width
    page_width = pdf.w - pdf.l_margin - pdf.r_margin
    total_pct = sum(col[2] for col in columns)
    col_widths = [(col[2] / total_pct) * page_width for col in columns]

    # Table header
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_fill_color(66, 133, 244)
    pdf.set_text_color(255, 255, 255)
    for i, col in enumerate(columns):
        pdf.cell(col_widths[i], 7, col[0], border=1, fill=True, align="C")
    pdf.ln()

    # Table rows
    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(0, 0, 0)

    for row_idx, record in enumerate(records):
        # Alternate row colors
        if row_idx % 2 == 0:
            pdf.set_fill_color(245, 245, 245)
        else:
            pdf.set_fill_color(255, 255, 255)

        row_height = 6
        for i, col in enumerate(columns):
            value = _extract_field(record, col[1])
            # Truncate long values
            max_chars = int(col_widths[i] / 1.8)
            if len(value) > max_chars:
                value = value[:max_chars - 2] + ".."
            pdf.cell(col_widths[i], row_height, _sanitize_text(value), border=1, fill=True)
        pdf.ln()

    # Footer
    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 7)
    pdf.cell(0, 5, f"Zoho CRM Export - {module}", align="C")

    # Write to temp file
    tmp_dir = tempfile.gettempdir()
    safe_title = "".join(c for c in title if c.isalnum() or c in " _-").strip()
    filename = f"{safe_title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(tmp_dir, filename)

    pdf.output(filepath)
    logger.info(f"PDF generated: {filepath} ({len(records)} records)")

    return filepath
