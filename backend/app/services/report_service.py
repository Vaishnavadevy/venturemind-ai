"""Professional, repeatable PDF report generation from a saved evaluation."""

from html import escape
from pathlib import Path
import re
from typing import Any

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.models.evaluation import Evaluation


class ReportService:
    """Generate a decision-support PDF without relying on client-side data."""

    def generate(self, evaluation: Evaluation, startup_name: str) -> Path:
        output = Path("output/pdf")
        output.mkdir(parents=True, exist_ok=True)
        safe_name = re.sub(r"[^a-z0-9]+", "-", startup_name.lower()).strip("-") or "startup"
        path = output / f"{safe_name}-evaluation-report.pdf"
        styles = getSampleStyleSheet()
        styles["Title"].textColor = HexColor("#4f46e5")
        styles.add(ParagraphStyle(name="ReportBody", parent=styles["BodyText"], leading=15, spaceAfter=7))
        styles.add(ParagraphStyle(name="ReportLabel", parent=styles["Heading3"], textColor=HexColor("#4f46e5"), spaceBefore=8))

        story = [
            Spacer(1, 4 * cm),
            Paragraph("VentureMind AI", styles["Title"]),
            Spacer(1, 0.4 * cm),
            Paragraph("Startup Evaluation Report", styles["Heading1"]),
            Spacer(1, 1 * cm),
            Paragraph(escape(startup_name), styles["Heading2"]),
            Spacer(1, 3 * cm),
            Paragraph(f"Overall confidence score: <b>{evaluation.overall_confidence_score or 'Not available'}/100</b>", styles["Heading1"]),
            Spacer(1, 0.5 * cm),
            Paragraph("Prepared from your saved startup submission and explainable evaluation factors.", styles["ReportBody"]),
            PageBreak(),
            Paragraph("Executive summary", styles["Heading1"]),
            Paragraph("This report documents the platform's explainable assessment of the submitted startup information. It supports founder decisions and customer research; it is not a guarantee of business success or investment outcomes.", styles["ReportBody"]),
            Spacer(1, 0.3 * cm),
            Paragraph("Explainable confidence scores", styles["Heading1"]),
        ]

        rows = [["Metric", "Score", "Reasoning"]] + [
            [escape(score.metric_key.replace("_", " ").title()), str(score.score), escape(score.reasoning)]
            for score in evaluation.scores
        ]
        table = Table(rows, colWidths=[3.8 * cm, 1.7 * cm, 10.5 * cm], repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#4f46e5")),
            ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#ffffff")),
            ("GRID", (0, 0), (-1, -1), 0.25, HexColor("#cbd5e1")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("LEADING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
        ]))
        story.append(table)

        sections: list[tuple[str, Any]] = [
            ("SWOT analysis", evaluation.swot_analysis),
            ("Business model canvas", evaluation.business_model_canvas),
            ("Market analysis", evaluation.market_analysis),
            ("Competitor analysis", evaluation.competitor_analysis),
            ("Risk analysis", evaluation.risk_analysis),
            ("Investment readiness", evaluation.investment_readiness),
            ("Startup roadmap", evaluation.roadmap),
            ("Financial forecast", evaluation.financial_forecast),
            ("Recommendations", evaluation.recommendations),
        ]
        for heading, content in sections:
            if content is not None:
                story.extend(self._section(heading, content, styles))

        document = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=1.5 * cm, leftMargin=1.5 * cm, topMargin=1.5 * cm, bottomMargin=1.5 * cm, title=f"VentureMind report - {startup_name}")
        document.build(story)
        return path

    def _section(self, heading: str, content: Any, styles: Any) -> list[Any]:
        blocks: list[Any] = [Spacer(1, 0.6 * cm), Paragraph(escape(heading), styles["Heading1"])]
        if isinstance(content, dict):
            for key, value in content.items():
                blocks.append(Paragraph(escape(str(key).replace("_", " ").title()), styles["ReportLabel"]))
                blocks.extend(self._content(value, styles))
        else:
            blocks.extend(self._content(content, styles))
        return blocks

    def _content(self, value: Any, styles: Any) -> list[Any]:
        if isinstance(value, list):
            blocks: list[Any] = []
            for item in value:
                if isinstance(item, dict):
                    blocks.append(Paragraph("; ".join(f"<b>{escape(str(key).replace('_', ' ').title())}</b>: {escape(str(item_value))}" for key, item_value in item.items()), styles["ReportBody"]))
                else:
                    blocks.append(Paragraph(f"• {escape(str(item))}", styles["ReportBody"]))
            return blocks or [Paragraph("No information recorded.", styles["ReportBody"])]
        return [Paragraph(escape(str(value)), styles["ReportBody"])]
