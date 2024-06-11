from datetime import datetime, timedelta
from typing import List, Dict

from fastapi import APIRouter, HTTPException, status, Body, Query
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
    "/unreturned/{storage_id}",
    response_description="List all reservations from specific storage that are unreturned",
    response_model_by_alias=False,
)
async def list_reservations(storage_id):
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
                'as': 'resource_details'
            }
        },
        {
            '$unwind': {
                'path': '$resource_details'
            }
        },
        {
            '$match': {
                '$and': [
                    {
                        'resource_details.storage_id': {
                            '$eq': storage_id
                        }
                    }, {
                        'return_date': {
                            '$eq': None
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
                'unreturnedCount': [
                    {
                        '$count': 'count'
                    }
                ],
                'unreturnedReservations': [
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
                'unreturnedCount': {
                    '$arrayElemAt': [
                        '$unreturnedCount.count', 0
                    ]
                },
                'unreturnedReservations': 1
            }
        }
    ]

    return await reservation_collection.aggregate(pipeline).to_list(None)

@router.get(
    "/detailed",
    response_description="List all reservations with additional details",
    response_model=List[Dict],
)
async def list_reservations_with_details():
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
                    }, {
                        '$project': {
                            '_id': 0
                        }
                    }
                ],
                'as': 'stock_item_details'
            }
        }, {
            '$addFields': {
                'stock_item_details': {
                    '$arrayElemAt': [
                        '$stock_item_details', 0
                    ]
                }
            }
        }, {
            '$lookup': {
                'from': 'resources',
                'let': {
                    'converted': {
                        '$toObjectId': '$stock_item_details.resource_id'
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
                    }, {
                        '$project': {
                            '_id': 0
                        }
                    }
                ],
                'as': 'resource_details'
            }
        }, {
            '$lookup': {
                'from': 'storages',
                'let': {
                    'converted': {
                        '$toObjectId': '$stock_item_details.storage_id'
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
                    }, {
                        '$project': {
                            '_id': 0
                        }
                    }
                ],
                'as': 'storage_details'
            }
        }, {
            '$addFields': {
                'resource_details': {
                    '$arrayElemAt': [
                        '$resource_details', 0
                    ]
                },
                'storage_details': {
                    '$arrayElemAt': [
                        '$storage_details', 0
                    ]
                }
            }
        }
    ]

    try:
        reservations_with_details = await reservation_collection.aggregate(pipeline).to_list(length=None)

        # Convert ObjectId to string
        for reservation in reservations_with_details:
            reservation['_id'] = str(reservation['_id'])
            reservation['stock_item_details']['resource_id'] = str(reservation['stock_item_details']['resource_id'])
            reservation['stock_item_details']['storage_id'] = str(reservation['stock_item_details']['storage_id'])

        return reservations_with_details
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
