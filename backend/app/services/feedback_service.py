from __future__ import annotations

from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.models.feedback import Feedback
from app.models.task import Task
from app.models.user import User
from app.services.business_id_service import (
    feedback_external_id,
    get_feedback_by_business_id,
    get_task_by_business_id,
    task_external_id,
    user_external_id,
)

VALID_FEEDBACK_STATUSES = {"pending", "processing", "completed"}


def _feedback_base_query(db: Session):
    return (
        db.query(Feedback)
        .options(
            selectinload(Feedback.user),
            selectinload(Feedback.handler),
            selectinload(Feedback.task).selectinload(Task.user),
        )
    )


def _resolve_task_filter(db: Session, task_id: str | None) -> int | None:
    if not task_id:
        return None
    task = get_task_by_business_id(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")
    return task.id


def _validate_feedback_content(content: str) -> str:
    normalized = (content or "").strip()
    if not normalized:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="反馈内容不能为空")
    if len(normalized) > 5000:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="反馈内容不能超过 5000 个字符")
    return normalized


def _validate_optional_text(value: str | None, field_label: str) -> str:
    normalized = (value or "").strip()
    if len(normalized) > 5000:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{field_label}不能超过 5000 个字符")
    return normalized


def _serialize_feedback(item: Feedback) -> dict:
    task = item.task
    task_user = task.user if task else None
    handler = item.handler
    return {
        "feedback_id": feedback_external_id(item),
        "user_id": user_external_id(item.user),
        "username": item.user.username if item.user else "",
        "task_id": task_external_id(task),
        "status": item.status or "pending",
        "content": item.content or "",
        "process_note": item.process_note or "",
        "result_note": item.result_note or "",
        "handler_id": user_external_id(handler) if handler else None,
        "handler_name": handler.username if handler else "",
        "handled_at": item.handled_at,
        "created_at": item.created_at,
        "updated_at": item.updated_at,
        "task_user_id": user_external_id(task_user),
        "task": {
            "task_id": task_external_id(task),
            "model": task.model if task else "",
            "mode": task.mode if task else "generate",
            "source": task.source if task else "web",
            "prompt": task.prompt if task else "",
            "status": task.status if task else "",
            "created_at": task.created_at if task else None,
        },
    }


def create_feedback(db: Session, user: User, task_id: str, content: str) -> dict:
    task = get_task_by_business_id(db, task_id)
    if not task or task.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")

    item = Feedback(
        user_id=user.id,
        task_id=task.id,
        content=_validate_feedback_content(content),
        status="pending",
    )
    db.add(item)
    db.commit()

    created = _feedback_base_query(db).filter(Feedback.id == item.id).first()
    if not created:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="反馈创建失败")
    return _serialize_feedback(created)


def list_feedbacks(
    db: Session,
    *,
    user_id: int | None = None,
    task_id: str | None = None,
    status_filter: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    query = _feedback_base_query(db)
    if user_id is not None:
        query = query.filter(Feedback.user_id == user_id)

    resolved_task_id = _resolve_task_filter(db, task_id)
    if resolved_task_id is not None:
        query = query.filter(Feedback.task_id == resolved_task_id)

    if status_filter:
        if status_filter not in VALID_FEEDBACK_STATUSES:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无效的反馈状态")
        query = query.filter(Feedback.status == status_filter)

    total = query.count()
    rows = (
        query.order_by(Feedback.created_at.desc(), Feedback.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {"total": total, "items": [_serialize_feedback(item) for item in rows]}


def get_feedback_detail(
    db: Session,
    feedback_id: str,
    *,
    user_id: int | None = None,
) -> dict:
    item = get_feedback_by_business_id(db, feedback_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="反馈不存在")
    if user_id is not None and item.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="反馈不存在")

    detail = _feedback_base_query(db).filter(Feedback.id == item.id).first()
    if not detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="反馈不存在")
    return _serialize_feedback(detail)


def update_feedback(
    db: Session,
    feedback_id: str,
    *,
    admin: User,
    status_value: str | None = None,
    process_note: str | None = None,
    result_note: str | None = None,
) -> dict:
    item = get_feedback_by_business_id(db, feedback_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="反馈不存在")

    if status_value is None and process_note is None and result_note is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="没有可更新的内容")

    if status_value is not None:
        if status_value not in VALID_FEEDBACK_STATUSES:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无效的反馈状态")
        item.status = status_value
        if status_value == "completed":
            item.handled_at = datetime.utcnow()
        else:
            item.handled_at = None

    if process_note is not None:
        item.process_note = _validate_optional_text(process_note, "处理进度")

    if result_note is not None:
        item.result_note = _validate_optional_text(result_note, "处理结果")

    item.handled_by = admin.id

    if item.status == "completed" and item.handled_at is None:
        item.handled_at = datetime.utcnow()

    db.add(item)
    db.commit()

    detail = _feedback_base_query(db).filter(Feedback.id == item.id).first()
    if not detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="反馈不存在")
    return _serialize_feedback(detail)
