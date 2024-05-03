import motor.motor_asyncio
from bson import ObjectId
from fastapi import FastAPI, status, HTTPException, Body
from pymongo import ReturnDocument

from models import Resource, Reservation, ReservationCollection, ResourceCollection, UpdateResource, UpdateReservation
from routers.stock_item_routes import router as stock_item_router
from routers.damage_routes import router as damage_router
from routers.storage_routes import router as storage_router
from routers.resource_routes import router as resource_router
from routers.reservation_routes import router as reservation_router

app = FastAPI(
    title="Student Course API",
    summary="A sample application showing how to use FastAPI to add a ReST API to a MongoDB collection.",
)

client = motor.motor_asyncio.AsyncIOMotorClient(
    "mongodb+srv://user_1:dCRoIQ3N95oU2fml@rentalservice.diaace4.mongodb.net/?retryWrites=true&w=majority")
db = client.rental_service
resource_collection = db.get_collection("resources")
damage_collection = db.get_collection("damages")
reservation_collection = db.get_collection("reservations")
storage_collection = db.get_collection("storages")
stock_item_collection = db.get_collection("stock_items")

app.include_router(stock_item_router, prefix="/stock-items", tags=["stock_items"])
app.include_router(damage_router, prefix="/damages", tags=["damages"])
app.include_router(storage_router, prefix="/storages", tags=["storages"])
app.include_router(resource_router, prefix="/resources", tags=["resources"])
app.include_router(reservation_router, prefix="/reservations", tags=["reservations"])

