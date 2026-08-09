from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from datetime import datetime
from typing import Dict, Any, Optional, List
import io

# ─────────────────────────────────────────────
# BRAND COLORS
# ─────────────────────────────────────────────
BRAND_BLUE = colors.HexColor("#1D4ED8")
BRAND_BLUE_LIGHT = colors.HexColor("#EFF6FF")
BRAND_BLUE_MID = colors.HexColor("#DBEAFE")
DARK = colors.HexColor("#0F172A")
DARK_MID = colors.HexColor("#1E293B")
GRAY_700 = colors.HexColor("#374151")
GRAY_500 = colors.HexColor("#6B7280")
GRAY_300 = colors.HexColor("#D1D5DB")
GRAY_100 = colors.HexColor("#F3F4F6")
GRAY_50 = colors.HexColor("#F9FAFB")
WHITE = colors.white
RED_700 = colors.HexColor("#B91C1C")
RED_100 = colors.HexColor("#FEE2E2")
RED_500 = colors.HexColor("#EF4444")
ORANGE_700 = colors.HexColor("#C2410C")
ORANGE_100 = colors.HexColor("#FFEDD5")
YELLOW_700 = colors.HexColor("#A16207")
YELLOW_100 = colors.HexColor("#FEF9C3")
GREEN_700 = colors.HexColor("#15803D")
GREEN_100 = colors.HexColor("#DCFCE7")
GREEN_500 = colors.HexColor("#22C55E")
BORDER = colors.HexColor("#E2E8F0")
SECTION_BG = colors.HexColor("#F8FAFC")


# ─────────────────────────────────────────────
# COLOR HELPERS
# ─────────────────────────────────────────────
def risk_color(level: str):
    l = (level or "").lower()
    if l in ("high", "critical"):
        return RED_500
    if l == "medium":
        return colors.HexColor("#F59E0B")
    if l == "low":
        return GREEN_500
    return GRAY_500


def risk_bg_color(level: str):
    l = (level or "").lower()
    if l in ("high", "critical"):
        return RED_100
    if l == "medium":
        return YELLOW_100
    if l == "low":
        return GREEN_100
    return GRAY_100


def risk_text_color(level: str):
    l = (level or "").lower()
    if l in ("high", "critical"):
        return RED_700
    if l == "medium":
        return YELLOW_700
    if l == "low":
        return GREEN_700
    return GRAY_500


# ─────────────────────────────────────────────
# SAFE STRING
# ─────────────────────────────────────────────
def safe_str(value, default="Not specified") -> str:
    if value is None:
        return default
    s = str(value).strip()
    if s in ("", "null", "None", "Unknown", "N/A"):
        return default
    return s


# ─────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────
def get_styles() -> dict:
    return {
        "h1": ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=22,
            textColor=DARK, spaceBefore=0, spaceAfter=6, leading=28),
        "h2": ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=14,
            textColor=DARK, spaceBefore=14, spaceAfter=6, leading=20),
        "h3": ParagraphStyle("h3", fontName="Helvetica-Bold", fontSize=11,
            textColor=DARK_MID, spaceBefore=10, spaceAfter=4, leading=16),
        "body": ParagraphStyle("body", fontName="Helvetica", fontSize=9,
            textColor=GRAY_700, leading=15, spaceAfter=5),
        "body_sm": ParagraphStyle("body_sm", fontName="Helvetica", fontSize=8,
            textColor=GRAY_700, leading=13, spaceAfter=4),
        "label": ParagraphStyle("label", fontName="Helvetica-Bold", fontSize=7,
            textColor=GRAY_500, leading=11, spaceAfter=2),
        "small": ParagraphStyle("small", fontName="Helvetica", fontSize=7,
            textColor=GRAY_500, leading=11, spaceAfter=2),
        "evidence": ParagraphStyle("evidence", fontName="Helvetica-Oblique", fontSize=8,
            textColor=GRAY_700, leading=13, leftIndent=8, spaceAfter=4),
        "bullet": ParagraphStyle("bullet", fontName="Helvetica", fontSize=9,
            textColor=GRAY_700, leading=15, leftIndent=12, spaceAfter=3,
            bulletIndent=4),
        "cover_brand": ParagraphStyle("cover_brand", fontName="Helvetica-Bold",
            fontSize=36, textColor=WHITE, alignment=TA_CENTER, leading=44),
        "cover_tagline": ParagraphStyle("cover_tagline", fontName="Helvetica",
            fontSize=11, textColor=colors.HexColor("#93C5FD"),
            alignment=TA_CENTER, leading=16),
        "cover_title": ParagraphStyle("cover_title", fontName="Helvetica-Bold",
            fontSize=20, textColor=DARK, alignment=TA_CENTER, leading=26),
        "cover_sub": ParagraphStyle("cover_sub", fontName="Helvetica",
            fontSize=11, textColor=GRAY_500, alignment=TA_CENTER, leading=16),
        "cover_meta_label": ParagraphStyle("cover_meta_label",
            fontName="Helvetica-Bold", fontSize=8, textColor=GRAY_500,
            alignment=TA_LEFT),
        "cover_meta_value": ParagraphStyle("cover_meta_value",
            fontName="Helvetica", fontSize=9, textColor=DARK,
            alignment=TA_LEFT),
        "toc": ParagraphStyle("toc", fontName="Helvetica", fontSize=10,
            textColor=DARK, leading=20),
        "toc_label": ParagraphStyle("toc_label", fontName="Helvetica-Bold",
            fontSize=8, textColor=GRAY_500, leading=14),
        "disclaimer": ParagraphStyle("disclaimer", fontName="Helvetica-Oblique",
            fontSize=7.5, textColor=GRAY_500, alignment=TA_CENTER, leading=12),
        "section_label": ParagraphStyle("section_label", fontName="Helvetica-Bold",
            fontSize=7, textColor=BRAND_BLUE, leading=10, spaceAfter=2),
        "table_header": ParagraphStyle("table_header", fontName="Helvetica-Bold",
            fontSize=8, textColor=WHITE, leading=12),
        "table_cell": ParagraphStyle("table_cell", fontName="Helvetica",
            fontSize=8, textColor=GRAY_700, leading=12),
        "table_cell_bold": ParagraphStyle("table_cell_bold",
            fontName="Helvetica-Bold", fontSize=8, textColor=DARK, leading=12),
    }


# ─────────────────────────────────────────────
# PAGE CANVAS WITH HEADER + FOOTER
# ─────────────────────────────────────────────
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._saved_page_states)
        for i, state in enumerate(self._saved_page_states):
            self.__dict__.update(state)
            self._draw_chrome(i + 1, total)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def _draw_chrome(self, page_num: int, total: int):
        if page_num == 1:
            return
        w, h = A4
        self.saveState()

        # Header bar
        self.setFillColor(DARK)
        self.rect(0, h - 18 * mm, w, 18 * mm, fill=1, stroke=0)
        self.setFillColor(WHITE)
        self.setFont("Helvetica-Bold", 8)
        self.drawString(20 * mm, h - 10 * mm, "ContractIQ")
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#94A3B8"))
        self.drawString(38 * mm, h - 10 * mm, "AI Contract Intelligence Platform")
        self.setFillColor(colors.HexColor("#64748B"))
        self.setFont("Helvetica-Bold", 7)
        self.drawRightString(w - 20 * mm, h - 10 * mm, "CONFIDENTIAL")

        # Footer bar
        self.setFillColor(GRAY_50)
        self.rect(0, 0, w, 14 * mm, fill=1, stroke=0)
        self.setStrokeColor(BORDER)
        self.setLineWidth(0.5)
        self.line(20 * mm, 14 * mm, w - 20 * mm, 14 * mm)
        self.setFillColor(GRAY_500)
        self.setFont("Helvetica", 7)
        self.drawString(20 * mm, 5 * mm,
            "This report is AI-generated and intended for informational purposes only. Not legal advice.")
        self.setFont("Helvetica-Bold", 7)
        self.setFillColor(DARK_MID)
        self.drawRightString(w - 20 * mm, 5 * mm, f"Page {page_num} of {total}")

        self.restoreState()


# ─────────────────────────────────────────────
# REUSABLE COMPONENTS
# ─────────────────────────────────────────────
def section_header(number: str, title: str, styles: dict) -> list:
    elements = [Spacer(1, 6 * mm)]
    # Section number + title row
    data = [[
        Paragraph(number, ParagraphStyle("sn", fontName="Helvetica-Bold",
            fontSize=10, textColor=WHITE)),
        Paragraph(title, ParagraphStyle("st", fontName="Helvetica-Bold",
            fontSize=12, textColor=WHITE))
    ]]
    t = Table(data, colWidths=[12 * mm, 158 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BRAND_BLUE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 4 * mm))
    return elements


def kv_table(rows: List[tuple], styles: dict, col1=55, col2=115) -> Table:
    data = []
    for k, v in rows:
        data.append([
            Paragraph(str(k), styles["label"]),
            Paragraph(safe_str(v), styles["body_sm"])
        ])
    t = Table(data, colWidths=[col1 * mm, col2 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), GRAY_50),
        ("BACKGROUND", (1, 0), (1, -1), WHITE),
        ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [GRAY_50, WHITE]),
    ]))
    return t


def risk_pill(level: str, styles: dict) -> Paragraph:
    return Paragraph(
        safe_str(level).upper(),
        ParagraphStyle("rp", fontName="Helvetica-Bold", fontSize=7,
            textColor=risk_text_color(level), leading=10)
    )


def bullet_list(items: list, styles: dict) -> list:
    elements = []
    for item in items:
        elements.append(Paragraph(f"&#8226;  {safe_str(item)}", styles["bullet"]))
    return elements


def divider(color=BORDER) -> HRFlowable:
    return HRFlowable(width="100%", thickness=0.5, color=color, spaceAfter=4)


# ─────────────────────────────────────────────
# COVER PAGE
# ─────────────────────────────────────────────
def build_cover(report: dict, styles: dict) -> list:
    meta = report.get("metadata", {})
    exec_data = (report.get("executive_summary") or {}).get("data") or {}
    file_name = safe_str(meta.get("file_name", "Contract"), "Contract")
    contract_type = safe_str(exec_data.get("contract_type"), "Contract Review")
    generated_at = safe_str(meta.get("generated_at",
        datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")))
    pages = safe_str(meta.get("page_count"))
    words = safe_str(meta.get("word_count"))
    ai_model = safe_str(meta.get("ai_model", "llama-3.3-70b-versatile"))
    w = A4[0] - 40 * mm

    elements = [Spacer(1, 20 * mm)]

    # Blue brand block
    brand_data = [[Paragraph("ContractIQ", styles["cover_brand"])]]
    brand_t = Table(brand_data, colWidths=[w])
    brand_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BRAND_BLUE),
        ("TOPPADDING", (0, 0), (-1, -1), 16),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(brand_t)

    # Tagline block
    tag_data = [[Paragraph("AI Contract Intelligence Platform", styles["cover_tagline"])]]
    tag_t = Table(tag_data, colWidths=[w])
    tag_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), DARK_MID),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    elements.append(tag_t)
    elements.append(Spacer(1, 14 * mm))

    # Report label
    elements.append(Paragraph("AI CONTRACT REVIEW REPORT", ParagraphStyle(
        "rl", fontName="Helvetica-Bold", fontSize=10,
        textColor=BRAND_BLUE, alignment=TA_CENTER, spaceAfter=4)))

    # Contract name
    display_name = file_name.replace(".pdf", "").replace("_", " ")
    elements.append(Paragraph(display_name, styles["cover_title"]))
    elements.append(Spacer(1, 2 * mm))
    elements.append(Paragraph(contract_type, styles["cover_sub"]))
    elements.append(Spacer(1, 10 * mm))
    elements.append(divider(BRAND_BLUE))
    elements.append(Spacer(1, 6 * mm))

    # Metadata grid
    meta_rows = [
        ("GENERATED", generated_at),
        ("AI MODEL", ai_model),
        ("DOCUMENT PAGES", pages),
        ("WORD COUNT", words),
        ("REVIEW TYPE", "Full AI Contract Analysis"),
        ("CLASSIFICATION", "Confidential"),
    ]
    grid_data = []
    row_pair = []
    for i, (k, v) in enumerate(meta_rows):
        cell = Table(
            [[Paragraph(k, styles["cover_meta_label"])],
             [Paragraph(safe_str(v), styles["cover_meta_value"])]],
            colWidths=[w / 2 - 4 * mm]
        )
        cell.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), GRAY_50),
            ("BOX", (0, 0), (-1, -1), 0.4, BORDER),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        row_pair.append(cell)
        if len(row_pair) == 2:
            grid_data.append(row_pair)
            row_pair = []
    if row_pair:
        row_pair.append(Spacer(1, 1))
        grid_data.append(row_pair)

    grid = Table(grid_data, colWidths=[w / 2 - 2 * mm, w / 2 - 2 * mm],
                 hAlign="CENTER")
    grid.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    elements.append(grid)
    elements.append(Spacer(1, 14 * mm))
    elements.append(divider())
    elements.append(Spacer(1, 4 * mm))
    elements.append(Paragraph(
        "This report was generated by ContractIQ AI and is intended solely for "
        "informational purposes. It does not constitute legal advice. "
        "Always consult a qualified legal professional before making decisions "
        "based on this analysis.",
        styles["disclaimer"]
    ))
    elements.append(PageBreak())
    return elements


# ─────────────────────────────────────────────
# TABLE OF CONTENTS
# ─────────────────────────────────────────────
def build_toc(styles: dict) -> list:
    elements = section_header("", "Table of Contents", styles)
    sections = [
        ("01", "Executive Summary"),
        ("02", "Contract Metadata"),
        ("03", "Executive Review"),
        ("04", "Review Findings"),
        ("05", "Clause Summary"),
        ("06", "Financial Review"),
        ("07", "Contract Timeline"),
        ("08", "Obligations"),
        ("09", "Final AI Recommendation"),
    ]
    data = [[
        Paragraph("NO.", styles["label"]),
        Paragraph("SECTION", styles["label"]),
    ]]
    for num, title in sections:
        data.append([
            Paragraph(num, ParagraphStyle("tn", fontName="Helvetica-Bold",
                fontSize=9, textColor=BRAND_BLUE)),
            Paragraph(title, styles["body"]),
        ])
    t = Table(data, colWidths=[20 * mm, 150 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, GRAY_50]),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(t)
    elements.append(PageBreak())
    return elements


# ─────────────────────────────────────────────
# EXECUTIVE SUMMARY
# ─────────────────────────────────────────────
def build_executive_summary(report: dict, styles: dict) -> list:
    elements = section_header("01", "Executive Summary", styles)
    exec_data = (report.get("executive_summary") or {}).get("data") or {}
    risk_data = (report.get("risk_findings") or {}).get("data") or {}
    ob_data = (report.get("obligations") or {}).get("data") or {}
    fin_data = (report.get("financial_review") or {}).get("data") or {}
    tl_data = (report.get("timeline") or {}).get("data") or {}
    rec_data = (report.get("final_recommendation") or {}).get("data") or {}

    if exec_data.get("summary"):
        elements.append(Paragraph(safe_str(exec_data["summary"]), styles["body"]))
        elements.append(Spacer(1, 4 * mm))

    overall_risk = safe_str(risk_data.get("overall_risk")) if risk_data else "N/A"
    quality = safe_str(rec_data.get("overall_quality")) if rec_data else "N/A"

    # Stats row
    stats = [
        ("Overall Risk", overall_risk),
        ("Contract Quality", quality),
        ("Risk Findings", str(risk_data.get("total_risks", 0)) if risk_data else "N/A"),
        ("Obligations", str(ob_data.get("total_obligations", 0)) if ob_data else "N/A"),
        ("Timeline Events", str(tl_data.get("total_events", 0)) if tl_data else "N/A"),
        ("Financial Fields", str(len([k for k in ["payment_amount","currency","deposit",
            "security_deposit","payment_schedule","billing_cycle","late_payment_penalty",
            "refund_policy","taxes","renewal_cost","interest","additional_charges"]
            if fin_data.get(k, {}).get("found")])) if fin_data else "N/A"),
    ]
    stat_data = []
    row = []
    for i, (label, value) in enumerate(stats):
        cell_data = [
            [Paragraph(label.upper(), styles["label"])],
            [Paragraph(value, ParagraphStyle("sv", fontName="Helvetica-Bold",
                fontSize=14, textColor=BRAND_BLUE, leading=18))]
        ]
        cell = Table(cell_data, colWidths=[45 * mm])
        cell.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), BRAND_BLUE_LIGHT),
            ("BOX", (0, 0), (-1, -1), 0.4, BRAND_BLUE_MID),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ]))
        row.append(cell)
        if len(row) == 3:
            stat_data.append(row)
            row = []
    if row:
        while len(row) < 3:
            row.append(Spacer(45 * mm, 1))
        stat_data.append(row)

    stat_t = Table(stat_data, colWidths=[47 * mm, 47 * mm, 47 * mm], hAlign="LEFT")
    stat_t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    elements.append(stat_t)
    elements.append(PageBreak())
    return elements


# ─────────────────────────────────────────────
# CONTRACT METADATA
# ─────────────────────────────────────────────
def build_metadata(report: dict, styles: dict) -> list:
    elements = section_header("02", "Contract Metadata", styles)
    meta = report.get("metadata") or {}
    exec_data = (report.get("executive_summary") or {}).get("data") or {}
    parties = exec_data.get("parties") or []

    rows = [
        ("File Name", meta.get("file_name")),
        ("File Size", meta.get("file_size")),
        ("Total Pages", meta.get("page_count")),
        ("Word Count", meta.get("word_count")),
        ("Contract Type", exec_data.get("contract_type")),
        ("Effective Date", exec_data.get("effective_date")),
        ("Duration", exec_data.get("duration")),
        ("Parties Identified", ", ".join(parties) if parties else None),
        ("Report Generated", meta.get("generated_at")),
        ("AI Model Used", meta.get("ai_model")),
        ("Review Classification", "Full Contract Analysis"),
    ]
    elements.append(kv_table(rows, styles))
    elements.append(PageBreak())
    return elements


# ─────────────────────────────────────────────
# EXECUTIVE REVIEW
# ─────────────────────────────────────────────
def build_executive_review(report: dict, styles: dict) -> list:
    elements = section_header("03", "Executive Review", styles)
    exec_data = (report.get("executive_summary") or {}).get("data") or {}

    if not exec_data:
        elements.append(Paragraph("Executive review data not available.", styles["body"]))
        elements.append(PageBreak())
        return elements

    if exec_data.get("summary"):
        elements.append(Paragraph("Overview", styles["h3"]))
        elements.append(Paragraph(safe_str(exec_data["summary"]), styles["body"]))
        elements.append(Spacer(1, 3 * mm))

    if exec_data.get("key_points"):
        elements.append(Paragraph("Key Points", styles["h3"]))
        elements += bullet_list(exec_data["key_points"], styles)
        elements.append(Spacer(1, 3 * mm))

    if exec_data.get("financial_terms"):
        elements.append(Paragraph("Financial Terms", styles["h3"]))
        elements.append(Paragraph(safe_str(exec_data["financial_terms"]), styles["body"]))
        elements.append(Spacer(1, 3 * mm))

    if exec_data.get("termination"):
        elements.append(Paragraph("Termination", styles["h3"]))
        elements.append(Paragraph(safe_str(exec_data["termination"]), styles["body"]))
        elements.append(Spacer(1, 3 * mm))

    if exec_data.get("risks"):
        elements.append(Paragraph("Key Risks Identified", styles["h3"]))
        elements += bullet_list(exec_data["risks"], styles)

    elements.append(PageBreak())
    return elements


# ─────────────────────────────────────────────
# REVIEW FINDINGS
# ─────────────────────────────────────────────
def build_risk_findings(report: dict, styles: dict) -> list:
    elements = section_header("04", "Review Findings", styles)
    risk_data = (report.get("risk_findings") or {}).get("data") or {}

    if not risk_data:
        elements.append(Paragraph("Risk findings not available.", styles["body"]))
        elements.append(PageBreak())
        return elements

    overall = safe_str(risk_data.get("overall_risk", "Unknown"))
    total = risk_data.get("total_risks", 0)
    high = len(risk_data.get("high_risks", []))
    medium = len(risk_data.get("medium_risks", []))
    low = len(risk_data.get("low_risks", []))

    summary_rows = [
        ("Overall Risk Level", overall),
        ("Total Findings", str(total)),
        ("High Risk", str(high)),
        ("Medium Risk", str(medium)),
        ("Low Risk", str(low)),
    ]
    elements.append(kv_table(summary_rows, styles, col1=55, col2=115))
    elements.append(Spacer(1, 4 * mm))

    all_risks = (risk_data.get("high_risks", []) +
                 risk_data.get("medium_risks", []) +
                 risk_data.get("low_risks", []))

    if all_risks:
        header = [
            Paragraph("FINDING", styles["table_header"]),
            Paragraph("SEVERITY", styles["table_header"]),
            Paragraph("EXPLANATION", styles["table_header"]),
        ]
        rows = [header]
        for r in all_risks:
            sev = safe_str(r.get("severity", r.get("risk_level", "Low")))
            rows.append([
                Paragraph(safe_str(r.get("label", r.get("title", ""))),
                    styles["table_cell_bold"]),
                Paragraph(sev.upper(), ParagraphStyle("sp",
                    fontName="Helvetica-Bold", fontSize=7,
                    textColor=risk_text_color(sev), leading=11)),
                Paragraph(safe_str(r.get("plain_english",
                    r.get("description", r.get("explanation", ""))))[:200],
                    styles["table_cell"]),
            ])
            clause = safe_str(r.get("clause", r.get("evidence", "")), "")
            if clause and clause != "Not specified":
                rows.append([
                    Paragraph("", styles["small"]),
                    Paragraph("", styles["small"]),
                    Paragraph(f'"{clause[:180]}"', styles["evidence"]),
                ])

        t = Table(rows, colWidths=[55 * mm, 22 * mm, 93 * mm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), DARK),
            ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, GRAY_50]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        elements.append(t)
    else:
        elements.append(Paragraph("No significant risk findings detected.", styles["body"]))

    elements.append(PageBreak())
    return elements


# ─────────────────────────────────────────────
# CLAUSE SUMMARY
# ─────────────────────────────────────────────
def build_clause_summary(report: dict, styles: dict) -> list:
    elements = section_header("05", "Clause Summary", styles)
    clause_section = report.get("clause_analysis") or {}

    if not clause_section.get("available") or not clause_section.get("data"):
        elements.append(Paragraph("Clause analysis not available for this report.", styles["body"]))
        elements.append(PageBreak())
        return elements

    clauses = clause_section["data"]
    if isinstance(clauses, dict):
        clauses = clauses.get("clauses", [])

    if not clauses:
        elements.append(Paragraph("No clauses extracted.", styles["body"]))
        elements.append(PageBreak())
        return elements

    header = [
        Paragraph("CLAUSE TITLE", styles["table_header"]),
        Paragraph("CATEGORY", styles["table_header"]),
        Paragraph("RISK", styles["table_header"]),
        Paragraph("PAGE", styles["table_header"]),
        Paragraph("EXPLANATION", styles["table_header"]),
    ]
    rows = [header]
    for c in clauses:
        rl = safe_str(c.get("risk_level", "Low"))
        rows.append([
            Paragraph(safe_str(c.get("title")), styles["table_cell_bold"]),
            Paragraph(safe_str(c.get("category")), styles["table_cell"]),
            Paragraph(rl.upper(), ParagraphStyle("rp2",
                fontName="Helvetica-Bold", fontSize=7,
                textColor=risk_text_color(rl), leading=11)),
            Paragraph(safe_str(c.get("page_number")), styles["table_cell"]),
            Paragraph(safe_str(c.get("plain_english", ""))[:180],
                styles["table_cell"]),
        ])

    t = Table(rows, colWidths=[38 * mm, 26 * mm, 14 * mm, 12 * mm, 80 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), DARK),
        ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, GRAY_50]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    elements.append(t)
    elements.append(PageBreak())
    return elements


# ─────────────────────────────────────────────
# FINANCIAL REVIEW
# ─────────────────────────────────────────────
def build_financial_review(report: dict, styles: dict) -> list:
    elements = section_header("06", "Financial Review", styles)
    fin_section = report.get("financial_review") or {}

    if not fin_section.get("available") or not fin_section.get("data"):
        elements.append(Paragraph("Financial review not available for this report.", styles["body"]))
        elements.append(PageBreak())
        return elements

    data = fin_section["data"]

    if data.get("financial_summary"):
        elements.append(Paragraph(safe_str(data["financial_summary"]), styles["body"]))
        elements.append(Spacer(1, 3 * mm))

    field_map = [
        ("payment_amount", "Payment Amount"),
        ("currency", "Currency"),
        ("deposit", "Deposit"),
        ("security_deposit", "Security Deposit"),
        ("payment_schedule", "Payment Schedule"),
        ("billing_cycle", "Billing Cycle"),
        ("late_payment_penalty", "Late Payment Penalty"),
        ("refund_policy", "Refund Policy"),
        ("taxes", "Taxes"),
        ("renewal_cost", "Renewal Cost"),
        ("interest", "Interest Rate"),
        ("additional_charges", "Additional Charges"),
    ]

    header = [
        Paragraph("FIELD", styles["table_header"]),
        Paragraph("VALUE", styles["table_header"]),
        Paragraph("RISK", styles["table_header"]),
        Paragraph("AI EXPLANATION", styles["table_header"]),
    ]
    rows = [header]

    for key, label in field_map:
        field = data.get(key) or {}
        found = field.get("found", False)
        value = safe_str(field.get("value")) if found else "Not found"
        rl = safe_str(field.get("risk_level", "Low"))
        explanation = safe_str(field.get("ai_explanation", ""))[:160]
        rows.append([
            Paragraph(label, styles["table_cell_bold"]),
            Paragraph(value, styles["table_cell"]),
            Paragraph(rl.upper(), ParagraphStyle("frp",
                fontName="Helvetica-Bold", fontSize=7,
                textColor=risk_text_color(rl) if found else GRAY_500,
                leading=11)),
            Paragraph(explanation, styles["table_cell"]),
        ])

    t = Table(rows, colWidths=[36 * mm, 26 * mm, 14 * mm, 94 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), DARK),
        ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, GRAY_50]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    elements.append(t)

    if data.get("hidden_risks"):
        elements.append(Spacer(1, 4 * mm))
        elements.append(Paragraph("Hidden Risks Detected", styles["h3"]))
        elements += bullet_list(data["hidden_risks"], styles)

    if data.get("missing_fields"):
        elements.append(Spacer(1, 3 * mm))
        elements.append(Paragraph("Missing Financial Information", styles["h3"]))
        elements.append(Paragraph(
            "The following fields were not found in this contract: " +
            ", ".join(data["missing_fields"]),
            styles["body"]
        ))

    elements.append(PageBreak())
    return elements


# ─────────────────────────────────────────────
# CONTRACT TIMELINE
# ─────────────────────────────────────────────
def build_timeline(report: dict, styles: dict) -> list:
    elements = section_header("07", "Contract Timeline", styles)
    tl_section = report.get("timeline") or {}

    if not tl_section.get("available") or not tl_section.get("data"):
        elements.append(Paragraph("Timeline data not available for this report.", styles["body"]))
        elements.append(PageBreak())
        return elements

    data = tl_section["data"]
    events = data.get("events") or []

    if data.get("summary"):
        elements.append(Paragraph(safe_str(data["summary"]), styles["body"]))
        elements.append(Spacer(1, 3 * mm))

    if not events:
        elements.append(Paragraph("No timeline events detected.", styles["body"]))
        elements.append(PageBreak())
        return elements

    header = [
        Paragraph("EVENT", styles["table_header"]),
        Paragraph("DATE / DURATION", styles["table_header"]),
        Paragraph("TYPE", styles["table_header"]),
        Paragraph("IMPORTANCE", styles["table_header"]),
        Paragraph("DESCRIPTION", styles["table_header"]),
    ]
    rows = [header]

    for e in events:
        imp = safe_str(e.get("importance", "Low"))
        rows.append([
            Paragraph(safe_str(e.get("title")), styles["table_cell_bold"]),
            Paragraph(safe_str(e.get("date_value")), styles["table_cell"]),
            Paragraph(safe_str(e.get("category")), styles["table_cell"]),
            Paragraph(imp.upper(), ParagraphStyle("ip",
                fontName="Helvetica-Bold", fontSize=7,
                textColor=risk_text_color(imp), leading=11)),
            Paragraph(safe_str(e.get("description", ""))[:160], styles["table_cell"]),
        ])

    t = Table(rows, colWidths=[35 * mm, 30 * mm, 22 * mm, 18 * mm, 65 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), DARK),
        ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, GRAY_50]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    elements.append(t)
    elements.append(PageBreak())
    return elements


# ─────────────────────────────────────────────
# OBLIGATIONS
# ─────────────────────────────────────────────
def build_obligations(report: dict, styles: dict) -> list:
    elements = section_header("08", "Obligations", styles)
    ob_section = report.get("obligations") or {}

    if not ob_section.get("available") or not ob_section.get("data"):
        elements.append(Paragraph("Obligations data not available for this report.", styles["body"]))
        elements.append(PageBreak())
        return elements

    data = ob_section["data"]
    obligations = data.get("obligations") or []

    if data.get("summary"):
        elements.append(Paragraph(safe_str(data["summary"]), styles["body"]))
        elements.append(Spacer(1, 3 * mm))

    if not obligations:
        elements.append(Paragraph("No obligations detected.", styles["body"]))
        elements.append(PageBreak())
        return elements

    parties: Dict[str, list] = {}
    for o in obligations:
        party = safe_str(o.get("responsible_party", "General Obligation"))
        parties.setdefault(party, []).append(o)

    for party, items in parties.items():
        elements.append(Paragraph(party, styles["h3"]))
        header = [
            Paragraph("OBLIGATION", styles["table_header"]),
            Paragraph("TYPE", styles["table_header"]),
            Paragraph("PRIORITY", styles["table_header"]),
            Paragraph("DEADLINE", styles["table_header"]),
            Paragraph("PAGE", styles["table_header"]),
        ]
        rows = [header]
        for o in items:
            pri = safe_str(o.get("priority", "Low"))
            deadline = safe_str(o.get("deadline"), "None stated")
            rows.append([
                Paragraph(safe_str(o.get("title")), styles["table_cell_bold"]),
                Paragraph(safe_str(o.get("obligation_type")), styles["table_cell"]),
                Paragraph(pri.upper(), ParagraphStyle("pp",
                    fontName="Helvetica-Bold", fontSize=7,
                    textColor=risk_text_color(pri), leading=11)),
                Paragraph(deadline, styles["table_cell"]),
                Paragraph(safe_str(o.get("page_hint")), styles["table_cell"]),
            ])

        t = Table(rows, colWidths=[55 * mm, 28 * mm, 18 * mm, 40 * mm, 29 * mm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), DARK_MID),
            ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, GRAY_50]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 4 * mm))

    elements.append(PageBreak())
    return elements


# ─────────────────────────────────────────────
# FINAL RECOMMENDATION
# ─────────────────────────────────────────────
def build_final_recommendation(report: dict, styles: dict) -> list:
    elements = section_header("09", "Final AI Recommendation", styles)
    rec_section = report.get("final_recommendation") or {}

    if not rec_section.get("available") or not rec_section.get("data"):
        elements.append(Paragraph("Final recommendation not available.", styles["body"]))
        elements.append(PageBreak())
        return elements

    data = rec_section["data"]

    if data.get("recommendation"):
        elements.append(Paragraph(safe_str(data["recommendation"]), styles["body"]))
        elements.append(Spacer(1, 4 * mm))

    if data.get("overall_quality"):
        elements.append(kv_table([("Overall Contract Quality",
            data["overall_quality"])], styles))
        elements.append(Spacer(1, 3 * mm))

    if data.get("major_risks"):
        elements.append(Paragraph("Major Risks", styles["h3"]))
        elements += bullet_list(data["major_risks"], styles)
        elements.append(Spacer(1, 3 * mm))

    if data.get("key_responsibilities"):
        elements.append(Paragraph("Key Responsibilities", styles["h3"]))
        elements += bullet_list(data["key_responsibilities"], styles)
        elements.append(Spacer(1, 3 * mm))

    if data.get("areas_for_legal_review"):
        elements.append(Paragraph("Areas Requiring Legal Review", styles["h3"]))
        elements += bullet_list(data["areas_for_legal_review"], styles)
        elements.append(Spacer(1, 6 * mm))

    # Final disclaimer box
    disclaimer_data = [[Paragraph(
        safe_str(data.get("disclaimer",
            "This AI-generated review is intended to assist document understanding "
            "and should not replace professional legal advice.")),
        styles["disclaimer"]
    )]]
    disc_t = Table(disclaimer_data, colWidths=[170 * mm])
    disc_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BRAND_BLUE_LIGHT),
        ("BOX", (0, 0), (-1, -1), 0.5, BRAND_BLUE),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    elements.append(disc_t)
    return elements


# ─────────────────────────────────────────────
# MAIN PDF GENERATOR
# ─────────────────────────────────────────────
def generate_pdf_report(report_data: Dict[str, Any]) -> bytes:
    buffer = io.BytesIO()
    styles = get_styles()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=22 * mm,
        bottomMargin=20 * mm,
    )

    elements = []

    builders = [
        lambda: build_cover(report_data, styles),
        lambda: build_toc(styles),
        lambda: build_executive_summary(report_data, styles),
        lambda: build_metadata(report_data, styles),
        lambda: build_executive_review(report_data, styles),
        lambda: build_risk_findings(report_data, styles),
        lambda: build_clause_summary(report_data, styles),
        lambda: build_financial_review(report_data, styles),
        lambda: build_timeline(report_data, styles),
        lambda: build_obligations(report_data, styles),
        lambda: build_final_recommendation(report_data, styles),
    ]

    for builder in builders:
        try:
            elements += builder()
        except Exception:
            pass

    doc.build(elements, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer.read()