#Standard Lib
import fastapi
import fastapi.staticfiles  #StaticFiles(静的ファイル用)
from fastapi import Request  #為保留原始程式碼所需
from fastapi.responses import FileResponse  #為保留原始程式碼所需

#3rd-party Lib
import dotenv  #load_dotenv()...環境変数(.env)の読み込みに必要
dotenv.load_dotenv()  #dotenvより後、全環境変数の読み込み

#Local Lib
#初期化目的：直接は呼び出さないが、app立ち上げと同時に全てのfileの内容がimportされる為処理が早くなる+構造の明確化
import config.log_config #特になし
import config.db_config #log_configより後
import handlers.exception_handlers as myexception #log_configより後
from controllers.mrt_contr import MrtRouter
from controllers.attraction_contr import AttractionRouter
from controllers.user_contr import UserRouter
from controllers.booking_contr import BookingRouter
from config.tappay_config import get_tappay_config


app = fastapi.FastAPI(
	title = "APIs for Taipei Day Trip",   #swaggerUIのタイトルなどの設定
	description = "台北一日遊網站 API 規格：網站後端程式必須支援這個 API 的規格，網站前端則根據 API 和後端互動。",
	version = "1.0.0",
	openapi_tags = [        #記述した順番通りにswaggerUiのtagsが表示される
		{"name": "User"},   #小文字、大文字はendポイントのtasの命名と一致させる必要あり。
		{"name": "Attraction"},
		{"name": "MRT Station"},
		{"name": "Booking"}
	]
)


app.include_router(AttractionRouter)
app.include_router(MrtRouter)
app.include_router(UserRouter)
app.include_router(BookingRouter)

app.mount("/static", fastapi.staticfiles.StaticFiles(directory="static"), name="static")

#modelで発生した例外も、ここで設定された例外ハンドラで処理される為modelに記述不要,特定のクラスに対するカスタムハンドラを登録
app.add_exception_handler(myexception.LoggerCritical, myexception.critical_err_handler)
app.add_exception_handler(fastapi.HTTPException, myexception.http_err_handler)
app.add_exception_handler(Exception, myexception.global_err_handler)


# Static Pages (Never Modify Code in this Block)
@app.get("/", include_in_schema=False)
async def index(request: Request):
	return FileResponse("./static/index.html", media_type="text/html")
@app.get("/attraction/{id}", include_in_schema=False)
async def attraction(request: Request, id: int):
	return FileResponse("./static/attraction.html", media_type="text/html")
@app.get("/booking", include_in_schema=False)
async def booking(request: Request):
	return FileResponse("./static/booking.html", media_type="text/html")
@app.get("/thankyou", include_in_schema=False)
async def thankyou(request: Request):
	return FileResponse("./static/thankyou.html", media_type="text/html")
# Static Pages (Never Modify Code in this Block)


@app.get("/api/tappay-config")
async def tappay_config():
	return get_tappay_config()



#3rd-party Lib
import pydantic
import datetime
import typing
from schemas.common_schemas import ResErrorSchema
from schemas.booking_schemas import AttractionItemSchema


class PostOrdersReqChild2Schema(pydantic.BaseModel):
	attraction: AttractionItemSchema
	date: datetime.date
	time: str

class BaseContactSchema(pydantic.BaseModel):
	name: str
	email: pydantic.EmailStr
	phone: int

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

class BasePaymentStatusSchema(pydantic.BaseModel):
	status: int
	message: str

class PostOrdersChild1Schema(pydantic.BaseModel):
	number: int    #pydanticのintはpyのintより広範囲をカバー、bigintと同等。
	payment: BasePaymentStatusSchema

class PostOrders200Schema(pydantic.BaseModel):
	data: PostOrdersChild1Schema

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



class GetOrderNumChild1Schema(PostOrdersChild1Schema):  #引数が持つprice, trip, contactを継承(合計5つ)
	number: int  #pydanticのintはpyのintより広範囲をカバー、bigintと同等。
	status: int

class GetOrderNum200Schema(pydantic.BaseModel):
	data: GetOrderNumChild1Schema

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

# class ReqTappaySchema(pydantic.BaseModel):
# 	prime: str
# 	partner_key: str
# 	merchant_id: str
# 	details: PostOrdersReqChild1Schema
# 	amount: int
# 	cardholder: BaseContactSchema
# 	remember: bool


from schemas.user_schemas import ResUserInfoSchema
import config.db_config as mydbconfig
import time
import random
import jwt
import httpx
import os
from fastapi.encoders import jsonable_encoder
import fastapi.encoders

@app.post("/api/orders",
	tags = ["Order"],
	summary = "建立新的訂單, 並完成付款程序",
	response_model = typing.Union[PostOrders200Schema, ResErrorSchema],
	responses = {
        200: {"model": PostOrders200Schema, "description": "訂單建立成功，包含付款狀態 ( 可能成功或失敗 )"},
        400: {"model": ResErrorSchema, "description": "訂單建立失敗，輸入不正確或其他原因"},
		403: {"model": ResErrorSchema, "description": "未登入系統, 拒絕存取"},
        500: {"model": ResErrorSchema, "description": "伺服器內部錯誤"}
	})
async def post_order_prime(req_body: PostOrdersReqSchema, authorization: str | None = fastapi.Header(None)) -> PostOrders200Schema:
	if (authorization is None):
		raise fastapi.HTTPException(status_code = 403, detail = "未登入系統, 拒絕存取")
	token = authorization.split(" ")[1] #jwtokenの値は：Bearer tokenとなっている故、spaceでsplitし、tokenのみ取得(Bearer除去)
	try:
		with open("static/taipei_day_trip_public_key.pem", "r") as file:
			public_key = file.read()
		decoded_token = jwt.decode(token, public_key, algorithms=["RS256"])
	except jwt.ExpiredSignatureError:  #期限切れの際にcatch
		print("超過有效期限")
	except jwt.InvalidTokenError:  #改ざんされた際にcatch
		print("無效的Token")
	user_id = decoded_token["user_id"]


	def generate_order_number_millisec():
		millisec = int(time.time() * 1000)
		random_digits = random.randint(0, 999)
		order_number = int(f"{millisec:013d}{random_digits:03d}")
		return order_number

	order_number = generate_order_number_millisec()

	with mydbconfig.connect_db() as db_conn:
		with db_conn.cursor(dictionary=True) as cursor:
			try:
				cursor.execute("""
					INSERT INTO orders
					(final_price, order_number, user_id)
					VALUES (%s, %s, %s)
				""",(req_body.order.price, order_number, user_id ))

				order_id = cursor.lastrowid  # 挿入されたordersのidを取得し以下でorder_itemsテーブルにデータを挿入

				cursor.execute("""
					INSERT INTO order_items
					(original_price, date, time, attraction_id, order_id)
					VALUES (%s, %s, %s, %s, %s)
                """, (req_body.order.price, req_body.order.trip.date,
                      req_body.order.trip.time, req_body.order.trip.attraction.id, order_id))

				db_conn.commit()
			except Exception as e:
				db_conn.rollback()
				raise Exception("SQL出問題:發生地=def save_payment_record-1") from e


	try:
		async with httpx.AsyncClient() as client:
			PARTNER_KEY = os.getenv("TAPPAY_PARTNER_KEY")
			MERCHANT_ID = os.getenv("TAPPAY_MERCHANT_ID")

			request_body = {  #tappayが要求するformatにしないとエラー
				"prime": req_body.prime,
				"partner_key": PARTNER_KEY,
				"merchant_id": MERCHANT_ID,
				"details": f"attraction_name:{req_body.order.trip.attraction.name}",  #detailsはstring(100)であることに注意
				"amount": 1,
				"cardholder": {
					"name": req_body.order.contact.name,
					"email": req_body.order.contact.email,
					"phone_number": req_body.order.contact.phone
				},
				"remember": False,
				"order_number": order_number,
			}

			request_header = {
					"Content-Type": "application/json",
					"x-api-key": PARTNER_KEY
			}

			#apiが求める形式をrequestする際は厳格なことが多い為、pydanticでjsonable_encoderしてもエラーになることが追い
			response = await client.post("https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime",
				json = request_body, headers = request_header, timeout = 30.0)

		result = response.json()
		print(result)
		print("===statuccheck===")
		if result["status"] == 0:  # 0 = 成功
			mark_order_as_paid(order_id)

			return PostOrders200Schema(
				data = {
					"number": order_number,
					"payment": {
						"status": 0,
						"message": "付款成功"
					}
				}
			)
		else:
			raise fastapi.HTTPException(status_code=400, detail="Payment processing failed = status not 0")
	except httpx.RequestError as e:
		raise fastapi.HTTPException(status_code=400, detail="Payment processing failed")


def mark_order_as_paid(order_id):
	with mydbconfig.connect_db() as db_conn:
		with db_conn.cursor(dictionary=True) as cursor:
			try:
				cursor.execute("""
					UPDATE orders
					JOIN order_items ON orders.id = order_items.order_id
				   	SET orders.payment_status = 1
				   	WHERE orders.payment_status = 0 AND order_items.order_id = %s;
				""",(order_id,))
				db_conn.commit()
			except Exception as e:
				db_conn.rollback()
				raise Exception("SQL出問題:發生地=def mark_order_as_paid-1") from e



@app.get("/api/order/{orderNumber}",
	tags = ["Order"],
	summary = "建立新的訂單, 並完成付款程序",
	response_model = typing.Union[GetOrderNum200Schema, ResErrorSchema],
	responses = {
        200: {"model": GetOrderNum200Schema, "description": "根據訂單編號取得訂單資訊，null 表示沒有資料"},
        403: {"model": ResErrorSchema, "description": "未登入系統, 拒絕存取"}
    })
async def get_order_num() -> GetOrderNum200Schema:
	pass