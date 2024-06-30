from schemas.common_schemas import ResErrorSchema
from schemas.attraction_schemas import ResAllAttractionSchema, ResDetailAttractionSchema
from models.attraction_model import AttractionModel
from views.attraction_view import AttractionView
import fastapi
import typing


AttractionRouter = fastapi.APIRouter()


@AttractionRouter.get("/api/attractions",
	tags = ["Attraction"],
    summary = "取得景點資料列表",
	response_model = typing.Union[ResAllAttractionSchema, ResErrorSchema],
	responses = {
		200: {"model": ResAllAttractionSchema, "description": "正常運作"},
		500: {"model": ResErrorSchema, "description": "伺服器內部錯誤"}
	}) #...は必須。ge=より大きいgreater than。Optionalをつけることで、str又はNoneどちらかを受け取れる。defaultはNone, キーワードの最小長が1文字
async def get_all(
	page: int = fastapi.Query(..., ge = 0, description = "要取得的分頁，每頁 12 筆資料"),
	keyword: str | None = fastapi.Query(
		None,   #Query()は第一引数に...を取れば必須、Noneを取れば空の意味。
		min_length = 1,  #値が提供された場合最低1文字以上(空文字は不許可)
	    description = "用來完全比對捷運站名稱、或模糊比對景點名稱的關鍵字，沒有給定則不做篩選"
)):
	size = 12
	attractions = AttractionModel.get_all(size, page, keyword)
	next_page = page + 1 if len(attractions) == size else None
	return AttractionView.render_all(next_page, attractions)


@AttractionRouter.get("/api/attraction/{attractionId}",
	tags = ["Attraction"],
    summary = "根據景點編號取得景點資料",
	response_model = typing.Union[ResDetailAttractionSchema, ResErrorSchema],
    responses = {
        200: {"model": ResDetailAttractionSchema, "description": "景點資料"},
        400: {"model": ResErrorSchema, "description": "景點編號不正確"},
        500: {"model": ResErrorSchema, "description": "伺服器內部錯誤"}
    })
async def get_detail(attractionId: int = fastapi.Path(description = "景點編號")):
	attraction = AttractionModel.get_detail(attractionId)
	return AttractionView.render_detail(attraction)