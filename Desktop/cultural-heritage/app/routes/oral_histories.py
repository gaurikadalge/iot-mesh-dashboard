# app/routes/oral_histories.py
from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId

from app.db.mongo import get_mongo_db
from app.models.oral_model import OralHistoryIn

router = APIRouter()


@router.get("/", summary="Get oral histories")
async def get_oral_histories(db=Depends(get_mongo_db)):
    try:
        collection = db["oral_histories"]
        cursor = collection.find({})
        items = await cursor.to_list(length=200)
        # convert ObjectId to string for front-end
        for item in items:
            item["_id"] = str(item["_id"])
        return {"count": len(items), "data": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", summary="Add oral history", status_code=status.HTTP_201_CREATED)
async def add_oral_history(payload: OralHistoryIn, db=Depends(get_mongo_db)):
    try:
        collection = db["oral_histories"]
        doc = payload.dict()
        res = await collection.insert_one(doc)
        return {"message": "Oral history added", "id": str(res.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{oid}", summary="Delete oral history")
async def delete_oral_history(oid: str, db=Depends(get_mongo_db)):
    try:
        collection = db["oral_histories"]
        result = await collection.delete_one({"_id": ObjectId(oid)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Record not found")
        return {"message": "Deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health():
    return {"status": "ok", "module": "oral_histories"}
