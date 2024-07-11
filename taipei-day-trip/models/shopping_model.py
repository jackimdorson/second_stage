# 初期段階ではshopping_model.pyに関連するモデルを定義し、プロジェクトの成長に応じて必要であれば分割を検討
#Standard Lib
import fastapi
import time
import random
import os

#3rd Lib
import httpx

#Local Lib
from schemas.shopping_schemas import PostBookingReqSchema, PostOrdersReqSchema
import config.db_config as mydbconfig


#booking_Endpoint
class BookingModel:
    @staticmethod
    def get_booking_info(decoded_jwt: str) -> dict | None:  #fetchOneは値がないこともある為, fetchOneはdefaultではtupleだが、dict=trueをしているため
        user_id = decoded_jwt.data.id

        with mydbconfig.connect_db() as db_conn:
            with db_conn.cursor(dictionary=True) as cursor:
                try:   #sqlは文1行ならスペース、複数行ならインデント。Select文の中のSelectはサブクエリでjoinでもできるが可読性が落ちる
                    cursor.execute("""
                        SELECT
                            cart.date, cart.time, cart.price,
                            a.id, a.name, a.address,
                            (SELECT images.url FROM images WHERE images.attraction_id = a.id LIMIT 1) AS img_url
                        FROM cart_items AS cart
                        INNER JOIN attractions AS a
                            ON cart.attraction_id = a.id
                        WHERE cart.user_id = %s
                        ORDER BY cart.updated_at DESC
                        LIMIT 1
                    """, (user_id,))
                    newest_item = cursor.fetchone()
                    return newest_item
                except Exception as e:
                    raise Exception("SQL出問題:發生地=def get_booking_info-1") from e


    @staticmethod
    def post_booking_info(cart: PostBookingReqSchema) -> bool:
        with mydbconfig.connect_db() as db_conn:
            with db_conn.cursor(dictionary=True) as cursor:
                try:
                    cursor.execute("""
                        INSERT INTO
                            cart_items (date, time, price, attraction_id, user_id)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (cart.date, cart.time, cart.price, cart.attractionId, cart.userId))
                    db_conn.commit()
                    return True
                except Exception as e:
                    db_conn.rollback()
                    raise Exception("SQL出問題:發生地=def post_booking_info-1") from e


    @staticmethod
    def delete_booking_info(decoded_jwt: str) -> bool:
        user_id = decoded_jwt.data.id

        with mydbconfig.connect_db() as db_conn:
            with db_conn.cursor(dictionary=True) as cursor:
                try:
                    cursor.execute("""
                        DELETE FROM cart_items
                        WHERE user_id = %s
                    """, (user_id,))
                    db_conn.commit()
                    return True
                except Exception as e:
                    db_conn.rollback()
                    raise Exception("SQL出問題:發生地=def delete_booking_info-1") from e


    #########多種購物車
    @staticmethod
    def get_cart_info(decoded_jwt: str) -> list | None:  #fetchOneは値がないこともある為
        user_id = decoded_jwt.data.id

        with mydbconfig.connect_db() as db_conn:
            with db_conn.cursor(dictionary=True) as cursor:
                try:   #sqlは文1行ならスペース、複数行ならインデント。Select文の中のSelectはサブクエリでjoinでもできるが可読性が落ちる
                    cursor.execute("""
                        SELECT
                            cart.date, cart.time, cart.price,
                            a.id, a.name, a.address,
                            (SELECT images.url FROM images WHERE images.attraction_id = a.id LIMIT 1) AS img_url
                        FROM cart_items AS cart
                        INNER JOIN attractions AS a
                            ON cart.attraction_id = a.id
                        WHERE cart.user_id = %s
                        ORDER BY cart.updated_at DESC
                    """, (user_id,))
                    all_items = cursor.fetchall()
                    return all_items
                except Exception as e:
                    raise Exception("SQL出問題:發生地=def get_booking_info-1") from e


    @staticmethod
    def delete_cart_info(decoded_jwt: str, item_id: int) -> bool:
        user_id = decoded_jwt.data.id

        with mydbconfig.connect_db() as db_conn:
            with db_conn.cursor(dictionary=True) as cursor:
                try:
                    cursor.execute("""
                        DELETE FROM cart_items
                        WHERE user_id = %s
                    """, (user_id,))
                    db_conn.commit()
                    return True
                except Exception as e:
                    db_conn.rollback()
                    raise Exception("SQL出問題:發生地=def delete_booking_info-1") from e



# Order_Endpoint
class OrderModel:
    @staticmethod
    async def create_order(decoded_jwt: str, req_body: PostOrdersReqSchema) -> int | None:
        user_id = decoded_jwt.data.id
        order_number = OrderModel.create_order_number()
        order_id = OrderModel.insert_getting_order_id(req_body, order_number, user_id)
        result = await OrderModel.reqres_tappay(req_body, order_number)
        if result["status"] == 0:  # 0 = 成功
            OrderModel.mark_order_as_paid(order_id)
            return order_number
        return None


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
                        (final_price, order_number, user_id, phone)
                        VALUES (%s, %s, %s, %s)
                    """,(req_body.order.price, order_number, user_id, req_body.order.contact.phone))

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


    @staticmethod
    def get_order_number(order_number: int) -> dict:
        with mydbconfig.connect_db() as db_conn:
            with db_conn.cursor(dictionary=True) as cursor:
                try:
                    cursor.execute("""
                        SELECT
                            o.payment_status, o.final_price, o.order_number, o.phone,
                            oitem.date, oitem.time,
                            a.id, a.name AS `a_name`,a.address,
                            users.name AS `user_name`, users.email,
                            (SELECT images.url FROM images WHERE images.attraction_id = a.id LIMIT 1) AS img_url
                        FROM
                            orders AS o
                        INNER JOIN
                            order_items AS oitem ON o.id = oitem.order_id
                        INNER JOIN
                            attractions AS a ON oitem.attraction_id = a.id
                        INNER JOIN
                            users ON o.user_id = users.id
                        WHERE
                            o.order_number = %s;
                    """,(order_number,))
                    return cursor.fetchone()  #fetchoneはなければNoneを返す
                except Exception as e:
                    raise Exception("SQL出問題:發生地=def get_order_number") from e
