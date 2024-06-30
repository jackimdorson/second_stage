import handlers.exception_handlers as myexception
import fastapi
import fastapi.staticfiles  #StaticFiles(静的ファイル用)
from fastapi.responses import FileResponse  #為保留原始程式碼所需
from fastapi import Request  #為保留原始程式碼所需
from fastapi.openapi.utils import get_openapi  #更改swaggerUI的Response順序所需
from controllers.mrt_contr import MrtRouter
from controllers.attraction_contr import AttractionRouter
from controllers.user_contr import UserRouter
from controllers.booking_contr import BookingRouter


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