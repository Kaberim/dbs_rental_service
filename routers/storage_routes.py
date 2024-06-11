from typing import List

from fastapi import APIRouter, HTTPException, status, Body
from bson import ObjectId
from pymongo import ReturnDocument
from models import Storage, UpdateStorage, StorageCollection, StorageSummary
import motor.motor_asyncio

router = APIRouter()
client = motor.motor_asyncio.AsyncIOMotorClient(
    "mongodb+srv://user_1:dCRoIQ3N95oU2fml@rentalservice.diaace4.mongodb.net/?retryWrites=true&w=majority")
db = client.rental_service
storage_collection = db.get_collection("storages")

@router.post(
    "/",
    response_description="Add new storage",
    response_model=Storage,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create_storage(storage: Storage):
    new_storage = await storage_collection.insert_one(
        storage.model_dump(by_alias=True, exclude=["id"])
    )
    created_storage = await storage_collection.find_one(
        {"_id": new_storage.inserted_id}
    )
    return created_storage

@router.get(
    "/",
    response_description="List all storages",
    response_model=StorageCollection,
    response_model_by_alias=False,
)
async def list_storages():
    storages = await storage_collection.find().to_list(1000)
    return StorageCollection(storages=storages)

@router.put(
    "/{id}",
    response_description="Update a storage",
    response_model=Storage,
    response_model_by_alias=False,
)
async def update_storage(id: str, storage: UpdateStorage = Body(...)):
    storage_data = {
        k: v for k, v in storage.model_dump(by_alias=True).items() if v is not None
    }

    if len(storage_data) >= 1:
        update_result = await storage_collection.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": storage_data},
            return_document=ReturnDocument.AFTER,
        )
        if update_result is not None:
            return update_result
        else:
            raise HTTPException(status_code=404, detail=f"Storage {id} not found")

    if (existing_storage := await storage_collection.find_one({"_id": id})) is not None:
        return existing_storage

    raise HTTPException(status_code=404, detail=f"Storage {id} not found")

@router.get("/summary", response_model=List[StorageSummary])
async def get_storage_summary():
    try:
        pipeline = [
            {
                "$lookup": {
                    "from": "stock_items",
                    "localField": "_id",
                    "foreignField": "storage_id",
                    "as": "stock_items"
                }
            },
            {
                "$lookup": {
                    "from": "reservations",
                    "localField": "stock_items._id",
                    "foreignField": "stock_item_id",
                    "as": "reservations"
                }
            },
            {
                "$lookup": {
                    "from": "damages",
                    "localField": "stock_items._id",
                    "foreignField": "stock_item_id",
                    "as": "damages"
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "total_reservations": {"$size": "$reservations"},
                    "total_stock_items": {"$size": "$stock_items"},
                    "total_damages": {"$size": "$damages"}
                }
            }
        ]

        cursor = storage_collection.aggregate(pipeline)
        storage_summaries = []

        async for item in cursor:
            storage_summaries.append(StorageSummary(
                storage_id=str(item["_id"]),
                total_reservations=item["total_reservations"],
                total_stock_items=item["total_stock_items"],
                total_damages=item["total_damages"]
            ))

        return storage_summaries

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))