#Standard LIb
import datetime

#3rd-party Lib
import pydantic


class ReqBookingSchema(pydantic.BaseModel):
    attractionId: int
    date: datetime.date
    time: str
    price: int
    userId: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "attractionId": 10,
                    "date": "2022-01-31",
                    "time": "afternoon",
                    "price": 2500
                }
            ]
        }
    }


class AttractionItemSchema(pydantic.BaseModel):
    id: int
    name: str
    address: str
    image: str


class cartItemSchema(pydantic.BaseModel):
    attraction: AttractionItemSchema
    date: datetime.date
    time: str
    price: int


class ReqCartSchema(pydantic.BaseModel):
    data: cartItemSchema | None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "data": {
                        "attraction": {
                            "id": 10,
                            "name": "平安鐘",
                            "address": "臺北市大安區忠孝東路 4 段",
                            "image": "https://yourdomain.com/images/attraction/10.jpg"
                        },
                        "date": "2022-01-31",
                        "time": "afternoon",
                        "price": 2500
                    }
                }
            ]
        }
    }


#########多種購物車
class ReqCartListSchema(pydantic.BaseModel):
    data: list[cartItemSchema] | None

    model_config = {
        "json_schema_extra" : {
            "examples": [
                {
                    "data": [
                        {
                            "attraction": {
                                "id": 10,
                                "name": "平安鐘",
                                "address": "臺北市大安區忠孝東路 4 段",
                                "image": "https://yourdomain.com/images/attraction/10.jpg"
                            },
                            "date": "2022-01-31",
                            "time": "afternoon",
                            "price": 2500
                        }
                    ]
                }
            ]
        }
    }