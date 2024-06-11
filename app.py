import motor.motor_asyncio
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from routers.damage_routes import router as damage_router
from routers.reservation_routes import router as reservation_router
from routers.resource_routes import router as resource_router
from routers.stock_item_routes import router as stock_item_router
from routers.storage_routes import router as storage_router

origins = [
    "http://localhost:4200",  # Your Angular app's URL
    # Add other origins if needed
]

app = FastAPI(
    title="Rental Service API",
    summary="A sample application showing how to use FastAPI to add a ReST API to a MongoDB collection.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

app.include_router(stock_item_router, prefix="/stock-items", tags=["stock_items"])
app.include_router(damage_router, prefix="/damages", tags=["damages"])
app.include_router(storage_router, prefix="/storages", tags=["storages"])
app.include_router(resource_router, prefix="/resources", tags=["resources"])
app.include_router(reservation_router, prefix="/reservations", tags=["reservations"])

