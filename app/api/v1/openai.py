import os
import uuid

from fastapi import APIRouter, Depends, HTTPException
from openai import AsyncOpenAI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.image import ImageSet

router = APIRouter(prefix="/openai", tags=["openai"])

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None


@router.post("/generate-anomaly/{image_id}")
async def generate_anomaly(
    image_id: int,
    prompt: str = "Add a subtle anomaly to this image",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not client:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")

    result = await db.execute(select(ImageSet).where(ImageSet.id == image_id))
    image = result.scalar_one_or_none()
    if not image:
        raise HTTPException(status_code=404, detail="Image set not found")
    if image.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    original_path = os.path.join(settings.UPLOAD_DIR, os.path.basename(image.original_url))
    if not os.path.exists(original_path):
        raise HTTPException(status_code=404, detail="Original file not found on disk")

    try:
        with open(original_path, "rb") as f:
            response = await client.images.edit(
                image=f,
                prompt=prompt,
                n=1,
                size="1024x1024",
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI error: {str(e)}")

    image_url = response.data[0].url
    if not image_url:
        raise HTTPException(status_code=500, detail="No image returned from OpenAI")

    # Download generated image
    import httpx

    async with httpx.AsyncClient() as http:
        r = await http.get(image_url)
        r.raise_for_status()
        ext = ".png"
        filename = f"{uuid.uuid4().hex}{ext}"
        filepath = os.path.join(settings.UPLOAD_DIR, filename)
        with open(filepath, "wb") as f:
            f.write(r.content)

    image.anomaly_url = f"/static/uploads/{filename}"
    await db.commit()
    await db.refresh(image)
    return {"anomaly_url": image.anomaly_url}
