from bson import ObjectId
from pydantic import BaseModel, Field
from typing import List, Optional


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class NodeModel (BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    text: Optional[str]
    childs: List = []

    def __getitem__(self, key):
        return getattr(self, key)

    class Config:
        allow_population_by_field_name = True
        arbirary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "id": "1",
                "text": "root",
                "childs": [
                    {
                        "id": "2",
                        "text": "child 1",
                        "childs": [
                            {
                                "id": "3",
                                "text": "child 1.1",
                                "childs": []
                            },
                            {
                                "id": "4",
                                "text": "child 1.2",
                                "childs": []
                            }
                        ]
                    },
                    {
                        "id": "5",
                        "text": "child 2",
                        "childs": []
                    }
                ]
            }
        }


class Leaf (BaseModel):
    path: str
    text: str

    def __getitem__(self, key):
        return getattr(self, key)


class TreeCreate (BaseModel):
    id: str

    def __getitem__(self, key):
        return getattr(self, key)
