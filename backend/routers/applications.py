from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from datetime import datetime
from database import get_db
from models import Application
from schemas import ApplicationCreate, ApplicationOut, ApplicationUpdate

router = APIRouter(prefix="/api/applications", tags=["applications"])

VALID_STATUSES = {"applied", "interview", "offer", "rejected"}


@router.get("/", response_model=List[ApplicationOut])
async def list_applications(status: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    q = select(Application).order_by(Application.updated_at.desc())
    if status:
        q = q.where(Application.status == status)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/", response_model=ApplicationOut)
async def create_application(body: ApplicationCreate, db: AsyncSession = Depends(get_db)):
    app = Application(
        **body.dict(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(app)
    await db.commit()
    await db.refresh(app)
    return app


@router.patch("/{app_id}", response_model=ApplicationOut)
async def update_application(app_id: int, body: ApplicationUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Application).where(Application.id == app_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    if body.status and body.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status. Use: {VALID_STATUSES}")
    for field, val in body.dict(exclude_none=True).items():
        setattr(app, field, val)
    app.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(app)
    return app


@router.delete("/{app_id}")
async def delete_application(app_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Application).where(Application.id == app_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Application not found")
    await db.execute(delete(Application).where(Application.id == app_id))
    await db.commit()
    return {"ok": True}
