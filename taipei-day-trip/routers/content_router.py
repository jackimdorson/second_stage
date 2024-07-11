#Standard Lib
import fastapi
import typing

#Local Lib
from schemas.common_schemas import ResErrorSchema
from schemas.content_schemas import GetAttractions200Schema, GetAttractionId200Schema, GetMrts200Schema
from models.content_model import AttractionModel, MrtModel
from views.content_view import AttractionView, MrtView


#関連するが、異なる責務のため、異なるRouterを使うことで、コードの組織化が可能。
AttractionRouter = fastapi.APIRouter(tags = ["Content"])
MrtRouter = fastapi.APIRouter(tags = ["Content"])  #rootingをmodule化(contrに分割)する時に必要になる



@AttractionRouter.get("/api/attractions/", summary = "取得景點資料列表", #queryのみurlから識別が難しい為、urlの最後に/をつけるとよい
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



@AttractionRouter.get("/api/attraction/{attractionId}", summary = "根據景點編號取得景點資料",
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



#mrt_Endpoint
@MrtRouter.get("/api/mrts",
    summary = "取得捷運站名稱列表",
	description = "取得所有捷運站名稱列表，按照週邊景點的數量由大到小排序",
    response_model = typing.Union[GetMrts200Schema, ResErrorSchema],  #このresponse2つの記述がないと、UI上には正常処理のみしか反映されない
	responses = {
		200: {"model": GetMrts200Schema, "description": "正常運作"},
		500: {"model": ResErrorSchema, "description": "伺服器內部錯誤"}
	})
async def get_mrts() -> GetMrts200Schema:  #正常処理のみ担当。MVCのどこかでErrorが発生 => exception_handlers.pyが担当(GetMrts200Schemaの返却は行われい)
	mrt_list = MrtModel.get_mrt_list()  #全体で一貫したエラーハンドリングが可能になり、個々のエンドポイントでのエラー処理の重複を避けれる＋同じファイルにある為集中的にログ記録や監視が可能に。
	return MrtView.render_mrt_list(mrt_list)