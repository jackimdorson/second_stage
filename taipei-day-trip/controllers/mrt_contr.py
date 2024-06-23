from models.mrt_model import MrtModel
from views.mrt_view import MrtView
import fastapi  #APIRouter()
import pydantic #BaseModel, Field(default値などの設定)
import typing   #Optional(値が指定された型または、Noneを受け入れるのに必要), List(list内の要素の型を指定するために使用), Union(2つの結合)


class MrtListSchema(pydantic.BaseModel):
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

class ErrorResponseSchema(pydantic.BaseModel):
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


MrtRouter = fastapi.APIRouter()  #rootingをmodule化(contrに分割)する時に必要になる


@MrtRouter.get("/api/mrts",
    response_model = typing.Union[MrtListSchema, ErrorResponseSchema],
	responses = {
		200: {"model": MrtListSchema, "description": "正常運作"},
		500: {"model": ErrorResponseSchema, "description": "伺服器內部錯誤"}
	})
async def get_mrt_list():
	mrt_list = MrtModel.get_mrt_list()
	return MrtView.render_mrt_list(mrt_list)