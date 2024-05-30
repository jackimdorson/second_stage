from common import app, logger, LoggerCritical, connect_db
from fastapi import Request, HTTPException, Query, Path
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Union  #Optional=値が指定された型または、Noneを受け入れるのに必要、List=list内の要素の型を指定するために使用
from decimal import Decimal
# import urllib.parse
# from starlette.middleware.sessions import SessionMiddleware
# app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))

class Attraction(BaseModel):  #pydanticの注意点：1.定義の順番、2.dbとの名称一致(asで取得)、3.データ型    dbの構造とは直接関係なく、APIの要件を満たすためのデータ構造を定義するためのもの=データの形式とバリデーションをを行う
	id: int
	name: str
	category: str
	description: str
	address: str
	transport: str
	mrt: str
	lat: Decimal
	lng: Decimal
	images: List[str]

class ResponseAttractions(BaseModel):
	data: List[Attraction] = Field(default_factory=list)
	nextPage: Optional[int] = Field(None, description="下一頁的編號。若沒有下一頁,則為null")
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

class ResponseAttractionId(BaseModel):   #Pydanticでは、フィールドに初期値を設定しない場合、そのフィールドは必須と見な
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

class ErrorResponseModel(BaseModel):
    error: bool
    message: str
    class Config:     #舊一點的寫法
        json_schema_extra = {
            "examples": [
                {
                    "error": True,
                    "message": "請按照情境提供對應的錯誤訊息"
                }
            ]
        }


class ResponseMrts(BaseModel):
	data: List[str]
	model_config = {
	"json_schema_extra": {
		"examples": [
			{
				"data": ["劍潭"]
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


@app.get("/api/attractions", response_model = Union[ResponseAttractions, ErrorResponseModel],
		responses = {
			200: {"model": ResponseAttractions, "description": "正常運作"},
			500: {"model": ErrorResponseModel, "description": "伺服器內部錯誤"}
		}) #...は必須。ge=より大きいgreater than。Optionalをつけることで、str又はNoneどちらかを受け取れる。defaultはNone, キーワードの最小長が1文字
async def get_pages(page: int = Query(..., ge=0, description="要取得的分頁，每頁 12 筆資料"), keyword: Optional[str] = Query(None, min_length=1, description="用來完全比對捷運站名稱、或模糊比對景點名稱的關鍵字，沒有給定則不做篩選")):
	size = 12
	with connect_db() as db_conn:
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
				raise HTTPException(status_code=404, detail={"error": True, "message": "無資料"})
			try:
				for attraction in attractions:
					cursor.execute("SELECT url FROM images WHERE attraction_id = %s", (attraction["id"],))
					attraction["images"] = [row["url"] for row in cursor.fetchall()]
			except Exception as e:
				raise Exception("SQL出問題:發生地=def get_pages-2") from e
			next_page = page + 1 if len(attractions) == size else None
			return {"nextPage": next_page, "data": attractions}
#raise = 意図的に例外を発生させ、処理を中断させる。try...except内で使用すると、exceptブロックでその例外を取得可能
#pathによる検索。

@app.get("/api/attractions/{attractionId}", response_model = Union[ResponseAttractionId, ErrorResponseModel],
		responses = {
			200: {"model": ResponseAttractionId, "description": "景點資料"},
			400: {"model": ErrorResponseModel, "description": "景點編號不正確"},
			500: {"model": ErrorResponseModel, "description": "伺服器內部錯誤"}
		})
async def get_attractions_info(attractionId: int = Path(description="景點編號")):
	with connect_db() as db_conn:
		with db_conn.cursor(dictionary=True) as cursor:
			if attractionId > 58:
				raise HTTPException(status_code=400, detail={"error": True, "message": "景點編號不正確, 請輸入低於58的整數"})
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
				raise HTTPException(status_code=400, detail={"error": True, "message": "景點編號不正確, 無資料"})
			try:
				cursor.execute("SELECT url FROM images WHERE attraction_id = %s", (attraction["id"],))
			except Exception as e:
				raise Exception("SQL出問題:發生地=def get_attractions-2") from e
			attraction["images"] = [row["url"] for row in cursor.fetchall()]
			return {"data": attraction}


@app.get("/api/mrts", response_model = Union[ResponseMrts, ErrorResponseModel],
		responses = {
			200: {"model": ResponseMrts, "description": "正常運作"},
			500: {"model": ErrorResponseModel, "description": "伺服器內部錯誤"}
		})
async def get_mrts():
	with connect_db() as db_conn:
		with db_conn.cursor(dictionary=True) as cursor:
			try:
				cursor.execute("""
					SELECT mrts.name, COUNT(a.id) AS a_count
					FROM mrts
					INNER JOIN attractions As a ON mrts.id = a.mrt_id
					GROUP BY mrts.name
					ORDER BY a_count DESC
				""")
			except Exception as e:
				raise Exception("SQL出問題:發生地=def get_mrts-1") from e
			mrts = [row["name"] for row in cursor.fetchall()]
			if not mrts:
				raise HTTPException(status_code=500, detail={"error": True, "message": "Not Found"})  #一般的には、データが見つからない場合には404を返すのが適切
			return {"data": mrts}