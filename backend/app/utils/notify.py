"""Send notifications when events happen."""
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Notification


async def send_notification(
    db: AsyncSession,
    user_id: UUID,
    type_: str,
    title: str,
    body: str = None,
    related_id: UUID = None,
):
    n = Notification(
        user_id=user_id, type=type_, title=title,
        body=body, related_id=related_id,
    )
    db.add(n)
    await db.flush()


async def notify_task_submitted(db: AsyncSession, child_name: str, parent_ids: list[UUID], task_title: str, task_id: UUID):
    for pid in parent_ids:
        await send_notification(db, pid, "submission",
            f"{child_name} 提交了「{task_title}」",
            f"请前往审核", task_id)


async def notify_task_reviewed(db: AsyncSession, child_id: UUID, task_title: str, status: str, note: str = None):
    text = "已通过 ✅" if status == "approved" else "已拒绝 ❌"
    await send_notification(db, child_id, "review",
        f"「{task_title}」{text}",
        note, None)


async def notify_application_reviewed(db: AsyncSession, child_id: UUID, title: str, status: str):
    text = "已通过 ✅" if status == "approved" else "已拒绝 ❌"
    await send_notification(db, child_id, "application",
        f"申请「{title}」{text}", None, None)


async def notify_redemption_reviewed(db: AsyncSession, child_id: UUID, reward_name: str, status: str):
    text = "已通过 ✅" if status == "approved" else "已拒绝 ❌"
    await send_notification(db, child_id, "redemption",
        f"兑换「{reward_name}」{text}", None, None)
