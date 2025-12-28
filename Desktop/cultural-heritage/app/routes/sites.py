# app/routes/sites.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
import csv
import json
from datetime import datetime

from app.db.postgres import get_postgres_session
from app.models.site_model import Site

router = APIRouter()

# ✅ Fetch all sites
@router.get("/", summary="Get all cultural sites")
async def get_sites(session: AsyncSession = Depends(get_postgres_session)):
    try:
        result = await session.execute(select(Site))
        sites = result.scalars().all()
        return [s.to_dict() for s in sites]
    except Exception as e:
        print(f"❌ Database error: {e}")
        return []

# ✅ Get single site by ID  
@router.get("/{site_id}", summary="Get site by ID")
async def get_site(site_id: int, session: AsyncSession = Depends(get_postgres_session)):
    try:
        result = await session.execute(select(Site).where(Site.site_id == site_id))
        site = result.scalars().first()
        if not site:
            raise HTTPException(status_code=404, detail="Site not found")
        return site.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching site: {e}")

# ✅ Add a new site
@router.post("/", summary="Add a new site", status_code=status.HTTP_201_CREATED)
async def add_site(data: dict, session: AsyncSession = Depends(get_postgres_session)):
    try:
        new_site = Site(
            name=data.get("name"),
            description=data.get("description"),
            location_city=data.get("location_city"),
            location_country=data.get("location_country"),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
        )
        session.add(new_site)
        await session.commit()
        await session.refresh(new_site)
        return {"message": "Site added successfully", "data": new_site.to_dict()}
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Error adding site: {e}")

# ✅ Update site
@router.put("/{site_id}", summary="Update site details")
async def update_site(site_id: int, data: dict, session: AsyncSession = Depends(get_postgres_session)):
    try:
        result = await session.execute(select(Site).where(Site.site_id == site_id))
        site = result.scalars().first()
        if not site:
            raise HTTPException(status_code=404, detail="Site not found")

        for field, value in data.items():
            if hasattr(site, field):
                setattr(site, field, value)

        await session.commit()
        await session.refresh(site)
        return {"message": "Site updated successfully", "data": site.to_dict()}
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating site: {e}")

# ✅ Delete site
@router.delete("/{site_id}", summary="Delete site by ID")
async def delete_site(site_id: int, session: AsyncSession = Depends(get_postgres_session)):
    try:
        result = await session.execute(select(Site).where(Site.site_id == site_id))
        site = result.scalars().first()
        if not site:
            raise HTTPException(status_code=404, detail="Site not found")

        await session.delete(site)
        await session.commit()
        return {"message": f"Site {site_id} deleted successfully"}
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting site: {e}")

# ✅ SEARCH SITES
@router.get("/search/", summary="Search sites by name")
async def search_sites(
    query: str = "", 
    session: AsyncSession = Depends(get_postgres_session)
):
    try:
        if not query:
            return []
        
        result = await session.execute(
            select(Site).where(Site.name.ilike(f"%{query}%"))
        )
        sites = result.scalars().all()
        return [s.to_dict() for s in sites]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {e}")

# ✅ EXPORT SITES TO CSV
@router.get("/export/csv", summary="Export sites to CSV")
async def export_sites_csv(session: AsyncSession = Depends(get_postgres_session)):
    try:
        result = await session.execute(select(Site))
        sites = result.scalars().all()
        
        if not sites:
            raise HTTPException(status_code=404, detail="No sites to export")
        
        # Convert to dict list
        sites_data = [s.to_dict() for s in sites]
        
        # Create CSV
        filename = f"cultural_sites_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            if sites_data:
                writer = csv.DictWriter(csvfile, fieldnames=sites_data[0].keys())
                writer.writeheader()
                writer.writerows(sites_data)
        
        return {
            "message": "Sites exported successfully", 
            "filename": filename,
            "count": len(sites_data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export error: {e}")

# ✅ Health check
@router.get("/health")
async def health():
    return {"status": "ok", "module": "sites"}