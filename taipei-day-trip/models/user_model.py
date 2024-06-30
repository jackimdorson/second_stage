from schemas.user_schemas import ReqSignUpSchema, ReqSignInSchema, ResJwtSchema
import config.db_config as mydbconfig
import passlib.context  #CryptContext(パスワードのハッシュ化と検証を行う)
import jwt
import datetime


pwd_context = passlib.context.CryptContext(schemes=["bcrypt"], deprecated="auto") #使用するアリゴリズムを指定、auto"に設定することで、bcryptが非推奨になった場合に自動的により安全なのに切り替える


class UserModel:
    def create_account(user: ReqSignUpSchema) -> bool:
        with mydbconfig.connect_db() as db_conn:
            with db_conn.cursor(dictionary=True) as cursor:
                try:
                    cursor.execute("""
                        SELECT email
                        FROM users
                        WHERE BINARY email = %s
                    """, (user.email,))
                    email_exists = cursor.fetchone()
                    if email_exists:
                        return False
                    hashed_password = pwd_context.hash(user.password)
                    cursor.execute("""
                        INSERT INTO users(name, email, password) VALUES(%s, %s, %s)
                    """, (user.name, user.email, hashed_password))
                    db_conn.commit()
                    return True
                except Exception as e:
                    db_conn.rollback()
                    raise Exception("SQL出問題:發生地=def create_account-1") from e


    def get_user_info(jwtoken: str | None) -> dict | None:
        if jwtoken is None:
            return None
        token = jwtoken.split(" ")[1]  #jwtokenの値は：Bearer tokenとなっている故、spaceでsplitし、tokenのみ取得(Bearer除去)
        try:
            with open("static/taipei_day_trip_public_key.pem", "r") as file:
                public_key = file.read()
            decoded_token = jwt.decode(token, public_key, algorithms=["RS256"])
            return decoded_token
        except jwt.ExpiredSignatureError:  #期限切れの際にcatch
            print("超過有效期限")
        except jwt.InvalidTokenError:  #改ざんされた際にcatch
            print("無效的Token")


    def get_jwt(signin: ReqSignInSchema) -> ResJwtSchema:
        with mydbconfig.connect_db() as db_conn:
            with db_conn.cursor(dictionary=True) as cursor:
                try:
                    cursor.execute("""
                        SELECT id, name, email, password
                        FROM users
                        WHERE BINARY email = %s
                    """, (signin.email,))
                    jwt_data = cursor.fetchone()
                except Exception as e:
                    raise Exception("SQL出問題:發生地=def get_jwt-1") from e
                if not jwt_data:
                    return False
                id, name, email, password = jwt_data.values()
                if not pwd_context.verify(signin.password, password):  #pwd_context.hashの検証にはverifyメソッドを使う、第一に普通のpsw,第二にhash済み
                    return False
                payload = {    	# jwtの生成
                    "user_id": id,
                    "user_name": name,
                    "email": email,
                    "iat": datetime.datetime.utcnow(),  #現在時刻を取得(=作成時刻)
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)  #現在時刻を取得し7日を足す
                }
                encoded_token = jwt.encode(payload, mydbconfig.private_key, algorithm = "RS256")
                return encoded_token