"""Authenticated generation and download of evaluation PDF reports."""

from datetime import UTC, datetime
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.dependencies import CurrentUser, DatabaseSession
from app.core.exceptions import ResourceNotFoundError
from app.models.enums import ReportStatus
from app.models.evaluation import Evaluation
from app.models.report import Report
from app.services.report_service import ReportService

router = APIRouter(prefix="/projects/{project_id}/evaluations/{evaluation_id}/report")


@router.post("")
def generate_report(
    project_id: str,
    evaluation_id: str,
    user: CurrentUser,
    session: DatabaseSession,
) -> FileResponse:
    evaluation = session.scalar(
        select(Evaluation)
        .options(selectinload(Evaluation.scores), selectinload(Evaluation.startup_idea))
        .where(Evaluation.id == evaluation_id, Evaluation.project_id == project_id)
    )
    if not evaluation or evaluation.project.owner_id != user.id:
        raise ResourceNotFoundError("Evaluation was not found.")
    path = ReportService().generate(evaluation, evaluation.startup_idea.startup_name)
    report = session.scalar(select(Report).where(Report.evaluation_id == evaluation.id))
    if report is None:
        report = Report(project_id=project_id, evaluation_id=evaluation.id)
        session.add(report)
    report.status = ReportStatus.READY
    report.storage_key = str(path)
    report.file_name = path.name
    report.mime_type = "application/pdf"
    report.file_size_bytes = path.stat().st_size
    report.generated_at = datetime.now(UTC)
    session.commit()
    return FileResponse(path, media_type="application/pdf", filename=path.name)


@router.get("/downloads/{report_id}")
def download_report(
    project_id: str,
    evaluation_id: str,
    report_id: str,
    user: CurrentUser,
    session: DatabaseSession,
) -> FileResponse:
    report = session.scalar(select(Report).where(
        Report.id == report_id,
        Report.project_id == project_id,
        Report.evaluation_id == evaluation_id,
    ))
    if not report or report.project.owner_id != user.id or not report.storage_key:
        raise ResourceNotFoundError("Report was not found.")
    path = Path(report.storage_key)
    if not path.is_file():
        raise ResourceNotFoundError("The generated report file is no longer available. Generate it again.")
    return FileResponse(path, media_type=report.mime_type or "application/pdf", filename=report.file_name or path.name)
