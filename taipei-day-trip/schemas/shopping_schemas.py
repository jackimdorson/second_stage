#Standard LIb
import datetime

#3rd-party Lib
import pydantic



#booking_Endpoint
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



#order_EndPoint
class BaseContactSchema(pydantic.BaseModel):
	name: str
	email: pydantic.EmailStr
	phone: str   #intだと最初の0973の0,+-が認識されない


class BasePaymentStatusSchema(pydantic.BaseModel):
	status: int
	message: str


class PostOrdersReqChild2Schema(pydantic.BaseModel):
	attraction: BaseBookingAttractionSchema
	date: datetime.date
	time: str


class PostOrdersReqChild1Schema(pydantic.BaseModel):
	price: int
	trip: PostOrdersReqChild2Schema
	contact: BaseContactSchema


class PostOrdersReqSchema(pydantic.BaseModel):
	prime: str
	order: PostOrdersReqChild1Schema

	model_config = {
		"json_schema_extra": {
			"examples": [
				{
					"prime": "前端從第三方金流 TapPay 取得的交易碼",
					"order": {
						"price": 2000,
						"trip": {
							"attraction": {
								"id": 10,
								"name": "平安鐘",
								"address": "臺北市大安區忠孝東路 4 段",
								"image": "https://yourdomain.com/images/attraction/10.jpg"
							},
							"date": "2022-01-31",
							"time": "afternoon"
						},
						"contact": {
							"name": "彭彭彭",
							"email": "ply@ply.com",
							"phone": "0912345678"
    					}
  					}
				}
			]
		}
	}


class PostOrders200Child1Schema(pydantic.BaseModel):
	number: int    #pydanticのintはpyのintより広範囲をカバー、bigintと同等。
	payment: BasePaymentStatusSchema


class PostOrders200Schema(pydantic.BaseModel):
	data: PostOrders200Child1Schema

	model_config = {
		"json_schema_extra": {
			"examples": [
				{
					"data": {
						"number": "20210425121135",
						"payment": {
							"status": 0,
							"message": "付款成功"
						}
					}
				}
			]
		}
	}


class GetOrderNum200Child1Schema(PostOrdersReqChild1Schema):  #引数が持つprice, trip, contactを継承(合計5つ)
	number: int  #pydanticのintはpyのintより広範囲をカバー、bigintと同等。
	status: int


class GetOrderNum200Schema(pydantic.BaseModel):
	data: GetOrderNum200Child1Schema | None

	model_config = {
		"json_schema_extra": {
			"examples": [
				{
					"data": {
						"number": "20210425121135",
						"price": 2000,
						"trip": {
							"attraction": {
								"id": 10,
								"name": "平安鐘",
								"address": "臺北市大安區忠孝東路 4 段",
								"image": "https://yourdomain.com/images/attraction/10.jpg"
							},
							"date": "2022-01-31",
							"time": "afternoon"
						},
						"contact": {
							"name": "彭彭彭",
							"email": "ply@ply.com",
							"phone": "0912345678"
						},
						"status": 1
					}
				}
			]
		}
	}