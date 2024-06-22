import handlers.exception_handlers as myexception
import config.db_config as mydbconfig
import fastapi
import fastapi.staticfiles  #StaticFiles(静的ファイル用)
import fastapi.encoders  #jsonable_encoder(jsonResponseの際、decimal型不支援の為 → float型に変更する際に()必要)
import fastapi.responses #JSONResponse, RedirectResponse(目前不用)
import jwt  #encode, decode, ExpiredSignatureError, InvalidTokenError
import datetime  #timedelta(引数に差分を取り、2つの時間差を表す), datetime.utcnow()(現在時刻の取得)
import decimal  #Decimal(dbの型で, pyには無いためimportが必要)
import pydantic #BaseModel, Field(default値などの設定)
import passlib.context  #CryptContext(パスワードのハッシュ化と検証を行う)
import typing  #Optional(値が指定された型または、Noneを受け入れるのに必要), List(list内の要素の型を指定するために使用), Union(2つの結合)
from fastapi.responses import FileResponse  #為保留原始程式碼所需
from fastapi import Request  #為保留原始程式碼所需

app = fastapi.FastAPI()
app.mount("/static", fastapi.staticfiles.StaticFiles(directory="static"), name="static")

app.add_exception_handler(myexception.LoggerCritical, myexception.critical_err_handler) #特定の例外クラスに対するカスタムハンドラを登録
app.add_exception_handler(fastapi.HTTPException, myexception.http_err_handler)
app.add_exception_handler(Exception, myexception.global_err_handler)

pwd_context = passlib.context.CryptContext(schemes=["bcrypt"], deprecated="auto") #使用するアリゴリズムを指定、auto"に設定することで、bcryptが非推奨になった場合に自動的により安全なのに切り替える

class Attraction(pydantic.BaseModel):  #pydanticの注意点：1.定義の順番、2.dbとの名称一致(asで取得)、3.データ型    dbの構造とは直接関係なく、APIの要件を満たすためのデータ構造を定義するためのもの=データの形式とバリデーションをを行う
	id: int
	name: str
	category: str
	description: str
	address: str
	transport: str
	mrt: str
	lat: decimal.Decimal
	lng: decimal.Decimal
	images: typing.List[str]

class User(pydantic.BaseModel):
	id: int
	name: str
	email: str

class ResponseAttractions(pydantic.BaseModel):
	nextPage: typing.Optional[int] = pydantic.Field(default=None, description="下一頁的編號。若沒有下一頁,則為null") #このフィールドは整数型で、値が存在しない場合はNoneを許容. デフォルト値をNoneに設定し、フィールドの説明を追加
	data: typing.List[Attraction] = pydantic.Field(default_factory=list) #listはmutableな為全てのインスタンスで共有されるのを防ぐ為、都度default値を生成する、default_factoryを使う。

	model_config = {     #この3行は固定。
		"json_schema_extra": {
			"examples": [
				{
					"nextPage": 1,
					"data": [
						{"id": 10, "name": "平安鐘", "category": "公共藝術", "description": "平安鐘祈求大家的平安，這是為了紀念 921 地震週年的設計", "address": " 臺北市大安區忠孝東路 4 段 1 號", "transport": "公車：204、212、212直", "mrt": "忠孝復興", "lat": 25.04181, "lng": 121.544814, "images" :["http://140.112.3.4/images/92-0.jpg"]}
					]
				}
			]
		}
	}

class ResponseAttractionId(pydantic.BaseModel):   #Pydanticでは、フィールドに初期値を設定しない場合、そのフィールドは必須と見な
	data: Attraction    #デフォルト値として空のリストを設定。各インスタンスが独自のリストを持つように。＝[]だと各自共通に

	model_config = {     #この3行は固定。最新寫法
		"json_schema_extra": {
			"examples": [
				{
					"data":
						{"id": 10, "name": "平安鐘", "category": "公共藝術", "description": "平安鐘祈求大家的平安，這是為了紀念 921 地震週年的設計", "address": " 臺北市大安區忠孝東路 4 段 1 號", "transport": "公車：204、212、212直", "mrt": "忠孝復興", "lat": 25.04181, "lng": 121.544814, "images" :["http://140.112.3.4/images/92-0.jpg"]}
				}
			]
		}
	}

class ErrorResponseModel(pydantic.BaseModel):
    error: bool
    message: str

    class Config:     #舊一點的寫法
        json_schema_extra = {      #json_schema_extra可顯示字, schema_extra只能顯示dataType, 故採取前者
            "examples": [
                {
                    "error": True,
                    "message": "請按照情境提供對應的錯誤訊息"
                }
            ]
        }


class ResponseMrts(pydantic.BaseModel):
	data: typing.List[str]

	model_config = {
		"json_schema_extra": {
			"examples": [
				{
					"data": ["劍潭"]
				}
			]
		}
	}

class UserCreateRequest(pydantic.BaseModel):
	name: str
	email: str
	password: str

	model_config = {
		"json_schema_extra": {
			"examples": [
				{
					"name": "彭彭彭",
  					"email": "ply@ply.com",
  					"password": "12345678"
				}
			]
		}
	}

class SuccessResponseModel(pydantic.BaseModel):
	ok: bool

	model_config = {
		"json_schema_extra": {
			"examples": [
				{
					"ok": True
				}
			]
		}
	}

class UserAuthResponse(pydantic.BaseModel):
	data: User

	model_config = {
		"json_schema_extra": {
			"examples": [
				{
                    "data": {
                        "id": 1,
                        "name": "彭彭彭",
                        "email": "ply@ply.com"
					}
				}
			]
		}
	}

class UserAuthRequest(pydantic.BaseModel):
	email: str
	password: str

	model_config = {
		"json_schema_extra": {
			"examples": [
				{
					"email": "ply@ply.com",
                    "password": "12345678"
				}
			]
		}
	}

class TokenResponseModel(pydantic.BaseModel):
	token: str

	model_config = {
		"json_schema_extra": {
			"examples": [
				{
					"token": "a21312xzDSADAsadasd8u32klKDFuSAD"
				}
			]
		}
	}

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
# ↑ Static Pages (Never Modify Code in this Block)


@app.get("/api/attractions", response_model = typing.Union[ResponseAttractions, ErrorResponseModel],
		responses = {
			200: {"model": ResponseAttractions, "description": "正常運作"},
			500: {"model": ErrorResponseModel, "description": "伺服器內部錯誤"}
		}) #...は必須。ge=より大きいgreater than。Optionalをつけることで、str又はNoneどちらかを受け取れる。defaultはNone, キーワードの最小長が1文字
async def get_pages(page: int = fastapi.Query(..., ge=0, description="要取得的分頁，每頁 12 筆資料"), keyword: typing.Optional[str] = fastapi.Query(None, min_length=1, description="用來完全比對捷運站名稱、或模糊比對景點名稱的關鍵字，沒有給定則不做篩選")):
	size = 12
	with mydbconfig.connect_db() as db_conn:
		with db_conn.cursor(dictionary=True) as cursor:  #預設tuple -> dictで返ってくる, cursorObjの生成が失敗することはない。
			try:
				if not keyword:
					cursor.execute("""
						SELECT a.id, a.name, categories.name AS category, a.description, a.address, a.transport, mrts.name AS mrt, a.latitude AS lat, a.longitude AS lng
						FROM attractions AS a
						INNER JOIN mrts ON a.mrt_id = mrts.id
						INNER JOIN categories ON a.category_id = categories.id
						ORDER BY a.id
						LIMIT %s OFFSET %s
					""",(size, page * size))    #LIKE"%keyword%"の形 keywordは二箇所に格納される
				else:
					cursor.execute("""
						SELECT a.id, a.name, categories.name AS category, a.description, a.address, a.transport, mrts.name AS mrt, a.latitude AS lat, a.longitude AS lng
						FROM attractions AS a
						INNER JOIN mrts ON a.mrt_id = mrts.id
						INNER JOIN categories ON a.category_id = categories.id
						WHERE mrts.name = %s OR a.name LIKE %s
						ORDER BY a.id
						LIMIT %s OFFSET %s
					""",(keyword, f"%{keyword}%", size, page * size))
			except Exception as e:
				raise Exception("SQL出問題:發生地=def get_pages-1") from e
			attractions = cursor.fetchall()     #返り値は　[ { },{ } ]  or  None
			if not attractions:
				raise fastapi.HTTPException(status_code=404, detail={"error": True, "message": "無資料"})
			try:
				for attraction in attractions:
					cursor.execute("SELECT url FROM images WHERE attraction_id = %s", (attraction["id"],))
					attraction["images"] = [row["url"] for row in cursor.fetchall()]
			except Exception as e:
				raise Exception("SQL出問題:發生地=def get_pages-2") from e
			next_page = page + 1 if len(attractions) == size else None
			return fastapi.responses.JSONResponse(content = fastapi.encoders.jsonable_encoder({"nextPage": next_page, "data": attractions}),
				headers = {"Content-Type": "application/json; charset=utf-8"})
#json.dumpsでエンコードした後にJSONResponseで再度エンコードすると、エスケープ文字（\）が追加される -> jsonable_encoderを使うと解決(decimal型→float型に)
#jsonResponseの際、decimal型不支援の為、 → float型に変更する際に必要
#raise = 意図的に例外を発生させ、処理を中断させる。try...except内で使用すると、exceptブロックでその例外を取得可能
#pathによる検索。

@app.get("/api/attraction/{attractionId}", response_model = typing.Union[ResponseAttractionId, ErrorResponseModel],
		responses = {
			200: {"model": ResponseAttractionId, "description": "景點資料"},
			400: {"model": ErrorResponseModel, "description": "景點編號不正確"},
			500: {"model": ErrorResponseModel, "description": "伺服器內部錯誤"}
		})
async def get_attractions_info(attractionId: int = fastapi.Path(description="景點編號")):
	with mydbconfig.connect_db() as db_conn:
		with db_conn.cursor(dictionary=True) as cursor:
			if attractionId > 58:
				raise fastapi.HTTPException(status_code=400, detail={"error": True, "message": "景點編號不正確, 請輸入低於58的整數"})
			try:
				cursor.execute("""
					SELECT a.id, a.name, categories.name AS category, a.description, a.address, a.transport, mrts.name AS mrt, a.latitude AS lat, a.longitude AS lng
					FROM attractions AS a
					INNER JOIN mrts ON a.mrt_id = mrts.id
					INNER JOIN categories ON a.category_id = categories.id
					WHERE a.id = %s
					ORDER BY a.id
				""",(attractionId,))            #%sの代入は例え、dictionary=Trueだとしても、tupleであることに注意。
			except Exception as e:
				raise Exception("SQL出問題:發生地=def get_attractions-1") from e
			attraction = cursor.fetchone()     #返り値は　{ }  or  None
			if attraction is None:    #fetchoneはなければNoneを返す、この記述は少しだけ高速。fetchallはListを返す為, if not attra...の記述法
				raise fastapi.HTTPException(status_code=400, detail={"error": True, "message": "景點編號不正確, 無資料"})
			try:
				cursor.execute("SELECT url FROM images WHERE attraction_id = %s", (attraction["id"],))
			except Exception as e:
				raise Exception("SQL出問題:發生地=def get_attractions-2") from e
			attraction["images"] = [row["url"] for row in cursor.fetchall()]
			return fastapi.responses.JSONResponse(content = fastapi.encoders.jsonable_encoder({"data": attraction}),
					headers = {"Content-Type": "application/json; charset=utf-8"})


@app.get("/api/mrts", response_model = typing.Union[ResponseMrts, ErrorResponseModel],
		responses = {
			200: {"model": ResponseMrts, "description": "正常運作"},
			500: {"model": ErrorResponseModel, "description": "伺服器內部錯誤"}
		})
async def get_mrts():
	with mydbconfig.connect_db() as db_conn:
		with db_conn.cursor(dictionary=True) as cursor:
			try:
				cursor.execute("""
					SELECT mrts.name, COUNT(a.id) AS a_count
					FROM mrts
					INNER JOIN attractions As a ON mrts.id = a.mrt_id
				    WHERE mrts.name != 'Unknown'
					GROUP BY mrts.name
					ORDER BY a_count DESC
				""")
			except Exception as e:
				raise Exception("SQL出問題:發生地=def get_mrts-1") from e
			mrts = [row["name"] for row in cursor.fetchall()]
			if not mrts:
				raise Exception("db出問題:發生地=def get_mrts-2")
			return fastapi.responses.JSONResponse(content={"data":mrts}, headers={"Content-Type": "application/json; charset=utf-8"})

# User登録(pswのhash化)：Union型の順序は重要ではありません。FastAPIはすべてのモデルに対してバリデーションを試み、最初に一致するモデルを使用
@app.post("/api/user", response_model = typing.Union[SuccessResponseModel, ErrorResponseModel],
		responses = {
			200: {"model": SuccessResponseModel, "description": "註冊成功"},
			400: {"model": ErrorResponseModel, "description": "註冊失敗, 重複的Email或其他原因"},
			500: {"model": ErrorResponseModel, "description": "伺服器內部錯誤"}
		})
async def create_user(user: UserCreateRequest):
	with mydbconfig.connect_db() as db_conn:
		with db_conn.cursor(dictionary=True) as cursor:
			try:
				cursor.execute("""
					SELECT email
				    FROM users
				    WHERE BINARY email = %s
				""", (user.email,))
				email_exists = cursor.fetchone()
			except Exception as e:
				raise Exception("SQL出問題:發生地=def create_user-1") from e
			if email_exists:
				raise fastapi.HTTPException(status_code=400, detail={"error": True, "message": "已被註冊過的Email"})
			try:
				hashed_password = pwd_context.hash(user.password)
				cursor.execute("""
					INSERT INTO users(name, email, password) VALUES(%s, %s, %s)
				""", (user.name, user.email, hashed_password))
				db_conn.commit()
				return fastapi.responses.JSONResponse(content={"ok":True}, headers={"Content-Type": "application/json; charset=utf-8"})
			except Exception as e:
				db_conn.rollback()
				raise Exception("SQL出問題:發生地=def create_user-1") from e

#JWTの検証(認証が必要なEndPoint用)＝取得已登入的會員資料
@app.get("/api/user/auth", response_model = UserAuthResponse,
		responses = {
			200: {"model": UserAuthResponse, "description": "已登入的會員資料, null 表示未登入"}
		})
async def get_user_auth(authorization: str = fastapi.Header(None)): #Header＝RequestHeaderからautho..を取得(defaultでは全て小文字に変換される故注意)なければNoneを返す
	if authorization is None:
		return fastapi.responses.JSONResponse(content={"data": None}, headers={"Content-Type": "application/json; charset=utf-8"})
	token = authorization.split(" ")[1]  #auth...の値は：Bearer tokenとなっている故、spaceでsplitし、tokenのみ取得(Bearer除去)
	try:
		with open("static/taipei_day_trip_public_key.pem", "r") as file:
			public_key = file.read()
		decoded = jwt.decode(token, public_key, algorithms=["RS256"])
		user_id, user_name, email, iat, exp = decoded.values()
		return fastapi.responses.JSONResponse(content={"data": {"id": user_id, "name": user_name, "email": email}}, headers={"Content-Type": "application/json; charset=utf-8"})
	except jwt.ExpiredSignatureError:  #期限切れの際にcatch
		print("超過有效期限")
		# return JSONResponse(content={"data": None}, headers={"Content-Type": "application/json; charset=utf-8"})
	except jwt.InvalidTokenError:  #改ざんされた際にcatch
		print("無效的Token")
		# return JSONResponse(content={"data": None}, headers={"Content-Type": "application/json; charset=utf-8"})



#登入成功，生產JWT
@app.put("/api/user/auth", response_model = typing.Union[TokenResponseModel, ErrorResponseModel],
		responses = {
			200: {"model": TokenResponseModel, "description": "登入成功，取得有效期為七天的 JWT 加密字串"},
			400: {"model": ErrorResponseModel, "description": "登入失敗，帳號或密碼錯誤或其他原因"},
			500: {"model": ErrorResponseModel, "description": "伺服器內部錯誤"}
		})
async def update_user_auth(auth: UserAuthRequest):
	with mydbconfig.connect_db() as db_conn:
		with db_conn.cursor(dictionary=True) as cursor:
			try:
				cursor.execute("""
					SELECT id, name, email, password
					FROM users
				    WHERE BINARY email = %s
				""", (auth.email,))
			except Exception as e:
				raise Exception("SQL出問題:發生地=def update_user_auth-1") from e
			jwt_data = cursor.fetchone()
			if not jwt_data:
				raise fastapi.HTTPException(status_code=400, detail={"error": True, "message": "帳號輸入錯誤"})
			id, name, email, password = jwt_data.values()
			if not pwd_context.verify(auth.password, password):  #pwd_context.hashの検証にはverifyメソッドを使う、第一に普通のpsw,第二にhash済み
				raise fastapi.HTTPException(status_code=400, detail={"error": True, "message": "密碼輸入錯誤"})
			payload = {    				# jwtの生成
				"user_id": id,
				"user_name": name,
				"email": email,
				"iat": datetime.datetime.utcnow(),  #現在時刻を取得(=作成時刻)
				"exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)  #現在時刻を取得し7日を足す
			}
			token = jwt.encode(payload, mydbconfig.private_key, algorithm="RS256")
			return fastapi.responses.JSONResponse(content={"token": token}, headers={"Content-Type": "application/json; charset=utf-8"})