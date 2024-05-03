from fastapi import APIRouter, HTTPException, status, Body
from bson import ObjectId
from pymongo import ReturnDocument
from models import Storage, UpdateStorage, StorageCollection
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