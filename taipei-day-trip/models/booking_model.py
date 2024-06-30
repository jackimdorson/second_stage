import config.db_config as mydbconfig
import jwt

class BookingModel:
    def get_booking_info(jwtoken):
        if jwtoken is None:
            return None
        token = jwtoken.split(" ")[1] #jwtokenの値は：Bearer tokenとなっている故、spaceでsplitし、tokenのみ取得(Bearer除去)
        try:
            with open("static/taipei_day_trip_public_key.pem", "r") as file:
                public_key = file.read()
            decoded_token = jwt.decode(token, public_key, algorithms=["RS256"])
        except jwt.ExpiredSignatureError:  #期限切れの際にcatch
            print("超過有效期限")
        except jwt.InvalidTokenError:  #改ざんされた際にcatch
            print("無效的Token")
        user_id = decoded_token["user_id"]

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
                    print(newest_item)
                    print("==xxx==")
                    return newest_item
                except Exception as e:
                    raise Exception("SQL出問題:發生地=def get_booking_info-1") from e


    def post_booking_info(cart):
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


    def delete_booking_info(jwtoken):
        if jwtoken is None:
            return None
        token = jwtoken.split(" ")[1] #jwtokenの値は：Bearer tokenとなっている故、spaceでsplitし、tokenのみ取得(Bearer除去)
        try:
            with open("static/taipei_day_trip_public_key.pem", "r") as file:
                public_key = file.read()
            decoded_token = jwt.decode(token, public_key, algorithms=["RS256"])
        except jwt.ExpiredSignatureError:  #期限切れの際にcatch
            print("超過有效期限")
        except jwt.InvalidTokenError:  #改ざんされた際にcatch
            print("無效的Token")
        user_id = decoded_token["user_id"]

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