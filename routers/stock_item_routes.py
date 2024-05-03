from fastapi import APIRouter, status, Body, HTTPException
from models import StockItem, StockItemCollection, UpdateStockItem
from pymongo import ReturnDocument
from bson import ObjectId
import motor.motor_asyncio

router = APIRouter()

client = motor.motor_asyncio.AsyncIOMotorClient(
    "mongodb+srv://user_1:dCRoIQ3N95oU2fml@rentalservice.diaace4.mongodb.net/?retryWrites=true&w=majority")
db = client.rental_service
stock_item_collection = db.get_collection("stock_items")
damage_collection = db.get_collection("damages")


@router.post(
    "/",
    response_description="Add new stock item",
    response_model=StockItem,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create_stock_item(stock_item: StockItem):
    new_stock_item = await stock_item_collection.insert_one(
        stock_item.model_dump(by_alias=True, exclude=["id"])
    )
    created_stock_item = await stock_item_collection.find_one(
        {"_id": new_stock_item.inserted_id}
    )
    return created_stock_item


@router.get(
    "/",
    response_description="List all stock items",
    response_model=StockItemCollection,
    response_model_by_alias=False,
)
async def list_stock_items():
    stock_items = await stock_item_collection.find().to_list(1000)
    return StockItemCollection(stock_items=stock_items)


@router.put(
    "/{id}",
    response_description="Update a stock item",
    response_model=StockItem,
    response_model_by_alias=False,
)
async def update_stock_item(id: str, stock_item: UpdateStockItem = Body(...)):
    stock_item_data = {
        k: v for k, v in stock_item.model_dump(by_alias=True).items() if v is not None
    }

    if len(stock_item_data) >= 1:
        update_result = await stock_item_collection.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": stock_item_data},
            return_document=ReturnDocument.AFTER,
        )
        if update_result is not None:
            return update_result
        else:
            raise HTTPException(status_code=404, detail=f"Stock item {id} not found")

    if (existing_stock_item := await stock_item_collection.find_one({"_id": id})) is not None:
        return existing_stock_item

    raise HTTPException(status_code=404, detail=f"Stock item {id} not found")


@router.get("/damaged/{id}")
async def get_stock_items_with_damages(stock_id: str):
    pipeline = [
        {
            '$match': {
                'storage_id': stock_id
            }
        },
        {
            '$lookup': {
                'from': 'damages',
                'let': {
                    'converted': {
                        '$toString': '$_id'
                    }
                },
                'pipeline': [
                    {
                        '$match': {
                            '$expr': {
                                '$eq': [
                                    '$$converted', '$stock_item_id'
                                ]
                            }
                        }
                    },
                    {
                        '$project': {
                            '_id': 0
                        }
                    }
                ],
                'as': 'damages'
            }
        },
        {
            '$match': {
                'damages': {'$ne': []}
            }
        },
        {
            '$lookup': {
                'from': 'resources',
                'let': {
                    'converted': {
                        '$toObjectId': '$resource_id'
                    }
                },
                'pipeline': [
                    {
                        '$match': {
                            '$expr': {
                                '$eq': [
                                    '$$converted', '$_id'
                                ]
                            }
                        }
                    },
                    {
                        '$project': {
                            '_id': 0
                        }
                    }
                ],
                'as': 'resource'
            }
        },
        {
            '$project': {
                '_id': 0
            }
        }

    ]

    return await stock_item_collection.aggregate(pipeline).to_list(None)
