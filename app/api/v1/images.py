import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.image import ImageSet
from app.models.anomaly_region import AnomalyRegion
from app.schemas.image import ImageSetOut, AnomalyRegionCreate, AnomalyRegionOut
from app.schemas.user import UserOut

router = APIRouter(prefix="/images", tags=["images"])


def save_upload(file: UploadFile) -> str:
    ext = os.path.splitext(file.filename or "")[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(file.file.read())
    return f"/static/uploads/{filename}"


@router.post("", response_model=ImageSetOut)
async def create_image_set(
    title: str = Form(...),
    description: str | None = Form(None),
    mutation_type: str = Form("none"),
    difficulty: int = Form(1),
    original: UploadFile = File(...),
    anomaly: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    original_url = save_upload(original)
    anomaly_url = save_upload(anomaly) if anomaly else original_url

    image_set = ImageSet(
        title=title,
        description=description,
        original_url=original_url,
        anomaly_url=anomaly_url,
        mutation_type=mutation_type,
        difficulty=difficulty,
        creator_id=current_user.id,
    )
    db.add(image_set)
    await db.commit()
    await db.refresh(image_set)

    result = await db.execute(
        select(ImageSet).options(selectinload(ImageSet.anomaly_regions), selectinload(ImageSet.creator)).where(ImageSet.id == image_set.id)
    )
    out = ImageSetOut.model_validate(result.scalar_one())
    out.creator_username = current_user.username
    return out


@router.get("", response_model=list[ImageSetOut])
async def list_image_sets(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ImageSet).options(selectinload(ImageSet.anomaly_regions), selectinload(ImageSet.creator)))
    images = result.scalars().all()
    outs = []
    for img in images:
        out = ImageSetOut.model_validate(img)
        out.creator_username = img.creator.username if img.creator else None
        print(f"DEBUG: img.id={img.id} creator_username={out.creator_username}")
        outs.append(out)
    return outs


@router.get("/{image_id}", response_model=ImageSetOut)
async def get_image_set(image_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ImageSet).options(selectinload(ImageSet.anomaly_regions), selectinload(ImageSet.creator)).where(ImageSet.id == image_id))
    image = result.scalar_one_or_none()
    if not image:
        raise HTTPException(status_code=404, detail="Image set not found")
    out = ImageSetOut.model_validate(image)
    out.creator_username = image.creator.username if image.creator else None
    return out


@router.post("/{image_id}/anomaly-regions", response_model=list[AnomalyRegionOut])
async def add_anomaly_regions(
    image_id: int,
    regions: list[AnomalyRegionCreate],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(ImageSet).where(ImageSet.id == image_id))
    image = result.scalar_one_or_none()
    if not image:
        raise HTTPException(status_code=404, detail="Image set not found")
    if image.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    if not regions:
        raise HTTPException(status_code=422, detail="At least one anomaly region is required")

    db_regions = []
    for region in regions:
        db_regions.append(
            AnomalyRegion(
                image_set_id=image_id,
                polygon=[point.model_dump() for point in region.polygon],
                order_index=region.order_index,
            )
        )
    db.add_all(db_regions)
    await db.commit()
    for db_region in db_regions:
        await db.refresh(db_region)
    return db_regions


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image_set(
    image_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ImageSet).options(selectinload(ImageSet.anomaly_regions)).where(ImageSet.id == image_id)
    )
    image = result.scalar_one_or_none()
    if not image:
        raise HTTPException(status_code=404, detail="Image set not found")
    if image.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Delete uploaded files
    for url in [image.original_url, image.anomaly_url]:
        if url:
            filepath = os.path.join(settings.UPLOAD_DIR, os.path.basename(url))
            if os.path.exists(filepath):
                os.remove(filepath)

    await db.delete(image)
    await db.commit()
    return None
