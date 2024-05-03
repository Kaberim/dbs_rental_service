from fastapi import APIRouter, HTTPException, status, Body
from bson import ObjectId
from pymongo import ReturnDocument
from models import Resource, UpdateResource, ResourceCollection
import motor.motor_asyncio

router = APIRouter()
client = motor.motor_asyncio.AsyncIOMotorClient(
    "mongodb+srv://user_1:dCRoIQ3N95oU2fml@rentalservice.diaace4.mongodb.net/?retryWrites=true&w=majority")
db = client.rental_service
resource_collection = db.get_collection("resources")

@router.post(
    "/",
    response_description="Add new resource",
    response_model=Resource,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create_resource(resource: Resource):
    new_resource = await resource_collection.insert_one(
        resource.model_dump(by_alias=True, exclude=["id"])
    )
    created_resource = await resource_collection.find_one(
        {"_id": new_resource.inserted_id}
    )
    return created_resource

@router.get(
    "/",
    response_description="List all resources",
    response_model=ResourceCollection,
    response_model_by_alias=False,
)
async def list_resources():
    resources = await resource_collection.find().to_list(1000)
    return ResourceCollection(resources=resources)

@router.put(
    "/{id}",
    response_description="Update a resource",
    response_model=Resource,
    response_model_by_alias=False,
)
async def update_resource(id: str, resource: UpdateResource = Body(...)):
    resource_data = {
        k: v for k, v in resource.model_dump(by_alias=True).items() if v is not None
    }

    if len(resource_data) >= 1:
        update_result = await resource_collection.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": resource_data},
            return_document=ReturnDocument.AFTER,
        )
        if update_result is not None:
            return update_result
        else:
            raise HTTPException(status_code=404, detail=f"Resource {id} not found")

    if (existing_resource := await resource_collection.find_one({"_id": id})) is not None:
        return existing_resource

    raise HTTPException(status_code=404, detail=f"Resource {id} not found")