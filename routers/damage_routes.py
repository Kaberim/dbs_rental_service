from fastapi import APIRouter, HTTPException, status, Body
from bson import ObjectId
from pymongo import ReturnDocument
from models import Damages, UpdateDamages, DamagesCollection
import motor.motor_asyncio

router = APIRouter()
client = motor.motor_asyncio.AsyncIOMotorClient(
    "mongodb+srv://user_1:dCRoIQ3N95oU2fml@rentalservice.diaace4.mongodb.net/?retryWrites=true&w=majority")
db = client.rental_service
damage_collection = db.get_collection("damages")

@router.post(
    "/",
    response_description="Add new damages",
    response_model=Damages,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create_damages(damages: Damages):
    new_damages = await damage_collection.insert_one(
        damages.model_dump(by_alias=True, exclude=["id"])
    )
    created_damages = await damage_collection.find_one(
        {"_id": new_damages.inserted_id}
    )
    return created_damages

@router.get(
    "/",
    response_description="List all damages",
    response_model=DamagesCollection,
    response_model_by_alias=False,
)
async def list_damages():
    damages = await damage_collection.find().to_list(1000)
    return DamagesCollection(damages=damages)

@router.put(
    "/{id}",
    response_description="Update a damage record",
    response_model=Damages,
    response_model_by_alias=False,
)
async def update_damage(id: str, damage: UpdateDamages = Body(...)):
    damage_data = {
        k: v for k, v in damage.model_dump(by_alias=True).items() if v is not None
    }

    if len(damage_data) >= 1:
        update_result = await damage_collection.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": damage_data},
            return_document=ReturnDocument.AFTER,
        )
        if update_result is not None:
            return update_result
        else:
            raise HTTPException(status_code=404, detail=f"Damage {id} not found")

    if (existing_damage := await damage_collection.find_one({"_id": id})) is not None:
        return existing_damage

    raise HTTPException(status_code=404, detail=f"Damage {id} not found")