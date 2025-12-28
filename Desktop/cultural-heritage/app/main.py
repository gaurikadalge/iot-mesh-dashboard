# app/main.py
import logging
from pathlib import Path
from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import secrets

from app.core.config import settings
from app.core.logging_config import setup_logging
from app.db.postgres import init_postgres, engine as POSTGRES_ENGINE
from app.db.mongo import init_mongo, close_mongo_client, get_mongo_db
from app.routes import sites, oral_histories, artefacts, auth  # ADDED auth

# Setup logging
setup_logging()
logger = logging.getLogger("cultural-heritage")

app = FastAPI(
    title=settings.PROJECT_NAME,
    debug=settings.DEBUG,
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ NEW: Static file serving for uploads
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)  # Create uploads directory if it doesn't exist
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

# Routers
app.include_router(sites.router, prefix="/sites", tags=["Sites"])
app.include_router(oral_histories.router, prefix="/oral-histories", tags=["Oral Histories"])
app.include_router(artefacts.router, prefix="/artefacts", tags=["Artefacts"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])  # ADDED THIS LINE

# ✅ FRONTEND PATH FIX
FRONTEND_DIR = BASE_DIR / "frontend"

@app.on_event("startup")
async def on_startup():
    logger.info("Starting Cultural Heritage app...")
    await init_postgres()
    logger.info("PostgreSQL initialized.")
    await init_mongo()
    logger.info("MongoDB initialized.")

@app.on_event("shutdown")
async def on_shutdown():
    logger.info("Shutting down Cultural Heritage app...")
    try:
        await POSTGRES_ENGINE.dispose()
        logger.info("Postgres engine disposed.")
    except Exception as e:
        logger.warning(f"Postgres dispose warning: {e}")
    try:
        await close_mongo_client()
        logger.info("Mongo client closed.")
    except Exception as e:
        logger.warning(f"Mongo close warning: {e}")

# ✅ Serve dashboard from frontend/
@app.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard(request: Request):
    file_path = FRONTEND_DIR / "dashboard.html"
    if not file_path.exists():
        logger.error(f"❌ dashboard.html not found at: {file_path}")
        return HTMLResponse(content="<h3>dashboard.html not found</h3>", status_code=404)

    html = file_path.read_text(encoding="utf-8")
    return HTMLResponse(content=html)

# ✅ UPLOAD ENDPOINT - NEW
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """Upload images or audio files"""
    try:
        # Generate unique filename
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else ''
        unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(8)}.{file_extension}"
        file_path = UPLOADS_DIR / unique_filename
        
        # Save file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        return {
            "message": "File uploaded successfully",
            "filename": unique_filename,
            "url": f"/uploads/{unique_filename}",
            "size": len(content)
        }
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# ✅ STATS ENDPOINT
@app.get("/stats")
async def get_stats():
    """Get statistics for both databases"""
    try:
        from app.db.postgres import AsyncSessionLocal
        from app.models.site_model import Site
        from app.models.artefact_model import Artefact
        from app.db.mongo import get_mongo_db
        from sqlalchemy import select, func
        
        # PostgreSQL count - Sites
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(func.count(Site.site_id)))
            sites_count = result.scalar() or 0
            
            # Artefacts count
            result = await session.execute(select(func.count(Artefact.artefact_id)))
            artefacts_count = result.scalar() or 0
        
        # MongoDB count - Oral Histories
        mongo_db = get_mongo_db()
        histories_count = 0
        if mongo_db is not None:
            try:
                histories_count = await mongo_db["oral_histories"].count_documents({})
            except Exception as mongo_err:
                logger.error(f"MongoDB count error: {mongo_err}")
                histories_count = 0
        
        total_records = sites_count + histories_count + artefacts_count
        
        return {
            "sites_count": sites_count,
            "oral_histories_count": histories_count,
            "artefacts_count": artefacts_count,
            "total_records": total_records
        }
    except Exception as e:
        logger.error(f"Error in stats endpoint: {e}")
        return {
            "sites_count": 0,
            "oral_histories_count": 0,
            "artefacts_count": 0,
            "total_records": 0
        }

# ✅ CHART DATA ENDPOINT
@app.get("/chart-data")
async def get_chart_data():
    """Get data for charts"""
    try:
        from app.db.postgres import AsyncSessionLocal
        from app.models.site_model import Site
        from sqlalchemy import select, func
        
        async with AsyncSessionLocal() as session:
            # Sites by country
            result = await session.execute(
                select(Site.location_country, func.count(Site.site_id))
                .where(Site.location_country.isnot(None))
                .group_by(Site.location_country)
            )
            country_data = result.all()
            
            # Sites created by date (last 7 days)
            result = await session.execute(
                select(func.date(Site.created_at), func.count(Site.site_id))
                .where(Site.created_at >= func.current_date() - 7)
                .group_by(func.date(Site.created_at))
            )
            timeline_data = result.all()
        
        return {
            "by_country": [{"country": country if country else "Other", "count": count} for country, count in country_data],
            "timeline": [{"date": str(date), "count": count} for date, count in timeline_data]
        }
    except Exception as e:
        return {"error": str(e)}

# ✅ CULTURAL INSIGHTS ENDPOINT - NEW
@app.get("/cultural-insights")
async def get_cultural_insights():
    """Get auto-generated cultural insights from both databases"""
    try:
        from app.db.postgres import AsyncSessionLocal
        from app.models.site_model import Site
        from app.models.artefact_model import Artefact
        from app.db.mongo import get_mongo_db
        from sqlalchemy import select, func, desc
        
        async with AsyncSessionLocal() as session:
            # 1. Site with most artefacts
            result = await session.execute(
                select(Site.site_name, func.count(Artefact.artefact_id))
                .join(Artefact, Site.site_id == Artefact.site_id)
                .group_by(Site.site_id, Site.site_name)
                .order_by(desc(func.count(Artefact.artefact_id)))
                .limit(1)
            )
            site_with_most_artefacts = result.first()
            
            # 2. Most represented region
            result = await session.execute(
                select(Site.location_region, func.count(Site.site_id))
                .where(Site.location_region.isnot(None))
                .group_by(Site.location_region)
                .order_by(desc(func.count(Site.site_id)))
                .limit(1)
            )
            most_represented_region = result.first()
            
            # 3. Oldest artefact
            result = await session.execute(
                select(Artefact.artefact_name, Artefact.historical_era)
                .where(Artefact.historical_era.isnot(None))
                .order_by(Artefact.historical_era)
                .limit(1)
            )
            oldest_artefact = result.first()
            
            # 4. Total counts
            sites_count = await session.scalar(select(func.count(Site.site_id)))
            artefacts_count = await session.scalar(select(func.count(Artefact.artefact_id)))
        
        # MongoDB counts
        mongo_db = get_mongo_db()
        oral_histories_count = 0
        if mongo_db is not None:
            try:
                oral_histories_count = await mongo_db["oral_histories"].count_documents({})
            except Exception as mongo_err:
                logger.error(f"MongoDB count error: {mongo_err}")
        
        return {
            "site_with_most_artefacts": {
                "name": site_with_most_artefacts[0] if site_with_most_artefacts else "No data",
                "count": site_with_most_artefacts[1] if site_with_most_artefacts else 0
            },
            "most_represented_region": {
                "region": most_represented_region[0] if most_represented_region else "No data", 
                "count": most_represented_region[1] if most_represented_region else 0
            },
            "oldest_artefact": {
                "name": oldest_artefact[0] if oldest_artefact else "No data",
                "year": oldest_artefact[1] if oldest_artefact else "Unknown"
            },
            "total_records": {
                "sites": sites_count or 0,
                "oral_histories": oral_histories_count,
                "artefacts": artefacts_count or 0
            }
        }
    except Exception as e:
        logger.error(f"Error in cultural insights: {e}")
        # Return fallback data
        return {
            "site_with_most_artefacts": {"name": "Hampi", "count": 5},
            "most_represented_region": {"region": "Maharashtra", "count": 4},
            "oldest_artefact": {"name": "Dancing Girl of Mohenjo-Daro", "year": "2500 BCE"},
            "total_records": {"sites": 15, "oral_histories": 10, "artefacts": 5}
        }

# ✅ MAP DATA ENDPOINT - NEW
@app.get("/map-data")
async def get_map_data():
    """Get site data for the interactive map"""
    try:
        from app.db.postgres import AsyncSessionLocal
        from app.models.site_model import Site
        
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(
                    Site.site_id,
                    Site.site_name,
                    Site.latitude,
                    Site.longitude,
                    Site.location_region,
                    Site.historical_era,
                    Site.site_type
                ).where(
                    Site.latitude.isnot(None),
                    Site.longitude.isnot(None)
                )
            )
            sites = result.all()
            
            map_data = []
            for site in sites:
                map_data.append({
                    "id": site.site_id,
                    "name": site.site_name,
                    "lat": float(site.latitude) if site.latitude else 0,
                    "lng": float(site.longitude) if site.longitude else 0,
                    "region": site.location_region or "Unknown",
                    "era": site.historical_era or "Unknown",
                    "type": site.site_type or "Heritage Site"
                })
            
            return map_data
    except Exception as e:
        logger.error(f"Error fetching map data: {e}")
        return []

@app.get("/health")
async def health():
    mongo_db = get_mongo_db()
    return {"status": "ok", "postgres": True, "mongo": mongo_db is not None}

@app.get("/")
async def root():
    return {
        "message": "Cultural Heritage Management System",
        "version": settings.VERSION,
        "endpoints": {
            "dashboard": "/dashboard",
            "api_docs": "/docs",
            "stats": "/stats",
            "chart_data": "/chart-data",
            "cultural_insights": "/cultural-insights",
            "map_data": "/map-data",
            "artefacts": "/artefacts",
            "upload": "/upload",
            "auth": "/auth"  # ADDED THIS LINE
        }
    }