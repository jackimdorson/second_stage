from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import json    #day-trip.jsonからのデータ取得必要

# import urllib.parse     #urllib.parseの利用に必要
# from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
import re






app=FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
# app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))

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



with open("taipei-attractions.json", "r", encoding="utf-8") as file:
	data = json.load(file)

def insert_data(attraction):
	sql = """
	INSERT INTO attractions (name, description, address, transport, rate, latitude, longitude)
	VALUES (%s, %s, %s, %s, %s, %s, %s)
	"""
	val = (
		attraction["name"],

	)