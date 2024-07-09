#3rd Lib
import jwt

#Local Lib
from schemas.booking_schemas import PostBookingReqSchema
import config.db_config as mydbconfig


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