#Standard Lib
import fastapi
import typing

#Local Lib
from schemas.common_schemas import ResErrorSchema
from schemas.attraction_schemas import GetAttractions200Schema, GetAttractionId200Schema
from models.attraction_model import AttractionModel
from views.attraction_view import AttractionView



AttractionRouter = fastapi.APIRouter(prefix = "/api", tags = ["Attraction"])



@AttractionRouter.get("/attractions/", summary = "取得景點資料列表", #queryのみurlから識別が難しい為、urlの最後に/をつけるとよい
	description="取得不同分頁的旅遊景點列表資料，也可以根據標題關鍵字、或捷運站名稱篩選",
	response_model = typing.Union[GetAttractions200Schema, ResErrorSchema],
	responses = {
		200: {"model": GetAttractions200Schema, "description": "正常運作"},
		500: {"model": ResErrorSchema, "description": "伺服器內部錯誤"}
	}
)
async def get_attractions(
	page: int = fastapi.Query(ge = 0, description = "要取得的分頁，每頁 12 筆資料"),
	keyword: str | None = fastapi.Query(None, min_length = 1, description = "用來完全比對捷運站名稱、或模糊比對景點名稱的關鍵字，沒有給定則不做篩選")
) -> GetAttractions200Schema:  #値が提供された場合最低1文字以上(空文字は不許可)
	size = 12
	attractions = AttractionModel.get_all(size, page, keyword)
	if not attractions:
		raise fastapi.HTTPException(status_code = 404, detail = "無資料")
	next_page = page + 1 if len(attractions) == size else None
	return AttractionView.render_all(next_page, attractions)



@AttractionRouter.get("/attraction/{attractionId}", summary = "根據景點編號取得景點資料",
	response_model = typing.Union[GetAttractionId200Schema, ResErrorSchema],
    responses = {
        200: {"model": GetAttractionId200Schema, "description": "景點資料"},
        400: {"model": ResErrorSchema, "description": "景點編號不正確"},
        500: {"model": ResErrorSchema, "description": "伺服器內部錯誤"}
    }
)
async def get_attractionid(attractionId: int = fastapi.Path(description = "景點編號")) -> GetAttractionId200Schema:
	attraction = AttractionModel.get_detail(attractionId)
	if not attraction:
		raise fastapi.HTTPException(status_code = 400, detail = "景點編號不正確, 無資料")
	return AttractionView.render_detail(attraction)