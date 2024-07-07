#Standard LIb
import datetime

#3rd-party Lib
import pydantic


class BaseBookingAttractionSchema(pydantic.BaseModel):
    id: int
    name: str
    address: str
    image: str


class PostBookingReqSchema(pydantic.BaseModel):
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


class GetCart200Child1Schema(pydantic.BaseModel):
    attraction: BaseBookingAttractionSchema
    date: datetime.date
    time: str
    price: int


class GetBooking200Schema(pydantic.BaseModel):
    data: GetCart200Child1Schema | None

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
class GetCart200Schema(pydantic.BaseModel):
    data: list[GetCart200Child1Schema] | None

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