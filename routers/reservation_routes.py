from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, status, Body
from bson import ObjectId
from pymongo import ReturnDocument
from models import Reservation, UpdateReservation, ReservationCollection
import motor.motor_asyncio

router = APIRouter()
client = motor.motor_asyncio.AsyncIOMotorClient(
    "mongodb+srv://user_1:dCRoIQ3N95oU2fml@rentalservice.diaace4.mongodb.net/?retryWrites=true&w=majority")
db = client.rental_service
reservation_collection = db.get_collection("reservations")


@router.post(
    "/",
    response_description="Add new reservation",
    response_model=Reservation,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create_reservation(reservation: Reservation):
    new_reservation = await reservation_collection.insert_one(
        reservation.model_dump(by_alias=True, exclude=["id"])
    )
    created_reservation = await reservation_collection.find_one(
        {"_id": new_reservation.inserted_id}
    )
    return created_reservation


@router.get(
    "/",
    response_description="List all reservations",
    response_model=ReservationCollection,
    response_model_by_alias=False,
)
async def list_reservations():
    reservations = await reservation_collection.find().to_list(1000)
    return ReservationCollection(reservations=reservations)


@router.put(
    "/{id}",
    response_description="Update a reservation",
    response_model=Reservation,
    response_model_by_alias=False,
)
async def update_reservation(id: str, reservation: UpdateReservation = Body(...)):
    reservation_data = {
        k: v for k, v in reservation.model_dump(by_alias=True).items() if v is not None
    }

    if len(reservation_data) >= 1:
        update_result = await reservation_collection.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": reservation_data},
            return_document=ReturnDocument.AFTER,
        )
        if update_result is not None:
            return update_result
        else:
            raise HTTPException(status_code=404, detail=f"Reservation {id} not found")

    if (existing_reservation := await reservation_collection.find_one({"_id": id})) is not None:
        return existing_reservation

    raise HTTPException(status_code=404, detail=f"Reservation {id} not found")


@router.get(
    "/overdue/{storage_id}",
    response_description="List all reservations from specific storage that are overdue",
    response_model_by_alias=False,
)
async def list_reservations(storage_id, days=14):
    filter_date = (datetime.now() - timedelta(days=int(days))).isoformat()
    pipeline = [
        {
            '$lookup': {
                'from': 'stock_items',
                'let': {
                    'converted': {
                        '$toObjectId': '$stock_item_id'
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
            '$unwind': {
                'path': '$resource'
            }
        },
        {
            '$match': {
                '$and': [
                    {
                        'resource.storage_id': {
                            '$eq': storage_id
                        }
                    }, {
                        'return_date': {
                            '$eq': None
                        }
                    },
                    {
                        '$expr': {
                            '$gt': [
                                '$booking_date', filter_date
                            ]
                        }
                    }
                ]
            }
        },
        {
            '$project': {
                '_id': 0
            }
        },
        {
            '$facet': {
                'overdueCount': [
                    {
                        '$count': 'count'
                    }
                ],
                'overdueReservations': [
                    {
                        '$sort': {
                            'booking_date': 1
                        }
                    }
                ]
            }
        },
        {
            '$project': {
                '_id': 0,
                'overdueCount': {
                    '$arrayElemAt': [
                        '$overdueCount.count', 0
                    ]
                },
                'overdueReservations': 1
            }
        }
    ]

    return await reservation_collection.aggregate(pipeline).to_list(None)
