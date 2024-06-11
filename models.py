from datetime import datetime
from typing import Optional, List, Annotated

from pydantic import Field, BaseModel, BeforeValidator

PyObjectId = Annotated[str, BeforeValidator(str)]


class Resource(BaseModel):
    """
    Container for a single resource record.
    """

    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    title: str = Field(..., alias="name")

    class Config:
        extra = "allow"
        json_schema_extra = {
            "example": {
                "id": "123",
                "title": "The Legend of Zelda: Breath of the Wild",
                "platform": "Nintendo Switch",
                "release_date": "2017-03-03",
                "developer": "Nintendo",
                "publisher": "Nintendo",
                "genre": ["Action-adventure", "Open-world"],
                "rating": "10/10",
            }
        }


class UpdateResource(BaseModel):
    """
    A set of optional updates to be made to a document in the database.
    """

    title: Optional[str] = None

    class Config:
        extra = "allow"
        json_schema_extra = {
            "example": {
                "title": "Updated Title",
                "platform": "Nintendo Switch",
                "release_date": "2022-01-01",
                "developer": "Updated Developer",
                "publisher": "Updated Publisher",
                "genre": ["Updated Genre"],
                "rating": "9/10",
            }
        }


class Storage(BaseModel):
    """
    Container for a single storage record.
    """

    id: Optional[PyObjectId] = Field(alias="_id", default=None)

    name: str = Field(...)
    address: str = Field(...)
    contact_number: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Warehouse A",
                "address": "123 Main Street",
                "contact_number": "+1234567890"
            }
        }


class UpdateStorage(BaseModel):
    """
    A set of optional updates to be made to a document in the database.
    """

    name: Optional[str] = None
    address: Optional[str] = None
    contact_number: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Updated Warehouse",
                "address": "Updated Address",
                "contact_number": "+987654321"
            }
        }


class StockItem(BaseModel):
    """
    Container for a single stock item record.
    """

    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    resource_id: str = Field(...)
    storage_id: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "resource_id": "123456789012345678901234",
                "storage_id": "123456789012345678901234"
            }
        }


class UpdateStockItem(BaseModel):
    """
    A set of optional updates to be made to a document in the database.
    """

    resource_id: Optional[str] = None
    storage_id: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "resource_id": "updated_resource_id",
                "storage_id": "updated_storage_id"
            }
        }


class Reservation(BaseModel):
    """
    Container for a single reservation record.
    """

    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    stock_item_id: str = Field(...)
    booking_date: datetime = Field(...)
    client_data: Optional[str] = None
    return_date: Optional[datetime] = None
    notes: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "stock_item_id": "123456789012345678901234",
                "booking_date": "2024-04-14T12:00:00",
                "client_data": "Client ABC",
                "return_date": "2024-04-21T12:00:00",
                "notes": "This is a reservation for Client ABC"
            }
        }


class UpdateReservation(BaseModel):
    """
    A set of optional updates to be made to a document in the database.
    """

    stock_item_id: Optional[str] = None
    booking_date: Optional[datetime] = None
    client_data: Optional[str] = None
    return_date: Optional[datetime] = None
    notes: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "stock_item_id": "updated_stock_item_id",
                "booking_date": "2024-04-15T12:00:00",
                "client_data": "Updated Client ABC",
                "return_date": "2024-04-22T12:00:00",
                "notes": "Updated reservation notes"
            }
        }


class Damages(BaseModel):
    """
    Container for a single damages record.
    """

    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    stock_item_id: str = Field(...)
    reservation_id: Optional[str] = None

    class Config:
        extra = "allow"
        json_schema_extra = {
            "example": {
                "stock_item_id": "123456789012345678901234",
                "reservation_id": "optional_reservation_id",
                "damage_type": "Scratch",
                "description": "Small scratch on the surface",
                "repair_cost": "50 USD"
            }
        }


class UpdateDamages(BaseModel):
    """
    A set of optional updates to be made to a document in the database.
    """

    stock_item_id: Optional[str] = None
    reservation_id: Optional[str] = None

    class Config:
        extra = "allow"
        json_schema_extra = {
            "example": {
                "stock_item_id": "updated_stock_item_id",
                "reservation_id": "updated_optional_reservation_id",
                "damage_type": "updated_damage_type",
                "description": "updated_description",
                "repair_cost": "updated_repair_cost"
            }
        }


class ResourceCollection(BaseModel):
    """
    A container holding a list of `ResourceModel` instances.
    """

    resources: List[Resource]


class StorageCollection(BaseModel):
    """
    A container holding a list of `StorageModel` instances.
    """

    storages: List[Storage]


class StockItemCollection(BaseModel):
    """
    A container holding a list of `StockItem` instances.
    """

    stock_items: List[StockItem]


class ReservationCollection(BaseModel):
    """
    A container holding a list of `Reservation` instances.
    """

    reservations: List[Reservation]


class DamagesCollection(BaseModel):
    """
    A container holding a list of `Damages` instances.
    """

    damages: List[Damages]


class StorageSummary(BaseModel):
    storage_id: str
    total_reservations: int
    total_stock_items: int
    total_damages: int