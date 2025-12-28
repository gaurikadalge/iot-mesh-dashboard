# app/routes/artefacts.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.postgres import get_postgres_session
from app.models.artefact_model import Artefact

router = APIRouter()

@router.get("/")
async def get_artefacts(session: AsyncSession = Depends(get_postgres_session)):
    """Get all artefacts"""
    try:
        result = await session.execute(select(Artefact))
        artefacts = result.scalars().all()
        return [artefact.to_dict() for artefact in artefacts]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching artefacts: {str(e)}")

@router.post("/")
async def create_artefact(artefact_data: dict, session: AsyncSession = Depends(get_postgres_session)):
    """Create a new artefact"""
    try:
        new_artefact = Artefact(**artefact_data)
        session.add(new_artefact)
        await session.commit()
        await session.refresh(new_artefact)
        return {"message": "Artefact created successfully", "data": new_artefact.to_dict()}
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating artefact: {str(e)}")

@router.delete("/{artefact_id}")
async def delete_artefact(artefact_id: int, session: AsyncSession = Depends(get_postgres_session)):
    """Delete an artefact"""
    try:
        result = await session.execute(select(Artefact).where(Artefact.artefact_id == artefact_id))
        artefact = result.scalar_one_or_none()
        
        if not artefact:
            raise HTTPException(status_code=404, detail="Artefact not found")
        
        await session.delete(artefact)
        await session.commit()
        return {"message": "Artefact deleted successfully"}
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting artefact: {str(e)}")