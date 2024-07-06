#Standard Lib
import fastapi
import time
import random
import os

#3rd-party Lib
import jwt
import httpx

#Local Lib
import config.db_config as mydbconfig
from schemas.order_schemas import PostOrdersReqSchema


class OrderModel:
    @staticmethod
    async def create_order(jwtoken: str, req_body: PostOrdersReqSchema) -> int | None:
        user_id = OrderModel.get_user_id(jwtoken)
        order_number = OrderModel.create_order_number()
        order_id = OrderModel.insert_getting_order_id(req_body, order_number, user_id)
        result = await OrderModel.reqres_tappay(req_body, order_number)
        if result["status"] == 0:  # 0 = 成功
            OrderModel.mark_order_as_paid(order_id)
            return order_number
        return None


    @staticmethod
    def get_user_id(jwtoken: str) -> int:
        token = jwtoken.split(" ")[1] #jwtokenの値は：Bearer tokenとなっている故、spaceでsplitし、tokenのみ取得(Bearer除去)
        try:
            with open("static/taipei_day_trip_public_key.pem", "r") as file:
                public_key = file.read()
            decoded_token = jwt.decode(token, public_key, algorithms=["RS256"])
            user_id = decoded_token["user_id"]
            return user_id

        except jwt.ExpiredSignatureError as e:  #期限切れの際にcatch
            raise fastapi.HTTPException(status_code = 400, detail = "JWT超過有效期限") from e
        except jwt.InvalidTokenError as e:  #改ざんされた際にcatch
            raise fastapi.HTTPException(status_code = 400, detail = "JWT簽名不一致") from e


    @staticmethod
    def create_order_number() -> int:
        millisec = int(time.time() * 1000)
        random_digits = random.randint(0, 999)
        order_number = int(f"{millisec:013d}{random_digits:03d}")
        return order_number


    @staticmethod
    def insert_getting_order_id(req_body: PostOrdersReqSchema, order_number: int, user_id: int) -> int:
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
                    return order_id

                except Exception as e:
                    db_conn.rollback()
                    raise Exception("SQL出問題:發生地 = def insert_getting_order_id") from e


    @staticmethod
    async def reqres_tappay(req_body: PostOrdersReqSchema, order_number: int):
        PARTNER_KEY = os.getenv("TAPPAY_PARTNER_KEY")
        MERCHANT_ID = os.getenv("TAPPAY_MERCHANT_ID")

        request_header = {
            "Content-Type": "application/json",
            "x-api-key": PARTNER_KEY
        }

        request_body = {  #tappayが要求するformatにしないとエラー(req_bodyは引数)
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
            "order_number": order_number
        }

        async with httpx.AsyncClient() as client:
            try:  #apiが求める形式をreqする際は厳格なことが多い為、pydanticでjsonable_encoderしてもエラーになることが追い
                response = await client.post("https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime",
                    json = request_body, headers = request_header, timeout = 30.0)
                print(f"Request Headerは{request_header}")
                return response.json()

            except httpx.RequestError as e:
                raise fastapi.HTTPException(status_code = 400, detail = "訂單建立失敗，輸入不正確或其他原因")


    @staticmethod
    def mark_order_as_paid(order_id: int) -> None:
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