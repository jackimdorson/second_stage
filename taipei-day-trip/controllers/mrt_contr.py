#Standard Lib
import fastapi  #APIRouter()
import typing   #List(list内の要素の型を指定するために使用), Union(2つの結合)

#Local Lib
from schemas.common_schemas import ResErrorSchema
from schemas.mrt_schemas import GetMrts200Schema
from models.mrt_model import MrtModel
from views.mrt_view import MrtView


MrtRouter = fastapi.APIRouter(prefix = "/api", tags = ["MRT Station"])  #rootingをmodule化(contrに分割)する時に必要になる


@MrtRouter.get("/mrts",
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