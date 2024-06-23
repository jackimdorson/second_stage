from models.attraction_model import AttractionModel
from views.attraction_view import AttractionView
import fastapi
import pydantic
import typing
import decimal  #Decimal(dbの型で, pyには無いためimportが必要)


class AttractionSchema(pydantic.BaseModel):  #pydanticの注意点：1.定義の順番、2.dbとの名称一致(asで取得)、3.データ型    dbの構造とは直接関係なく、APIの要件を満たすためのデータ構造を定義するためのもの=データの形式とバリデーションをを行う
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

class AllAttractionSchema(pydantic.BaseModel):
	nextPage: typing.Optional[int] = pydantic.Field(
		default = None,
		description = "下一頁的編號。若沒有下一頁,則為null"
	) #このフィールドは整数型で、値が存在しない場合はNoneを許容. デフォルト値をNoneに設定し、フィールドの説明を追加
	data: typing.List[AttractionSchema] = pydantic.Field(default_factory = list) #listはmutableな為全てのインスタンスで共有されるのを防ぐ為、都度default値を生成する、default_factoryを使う。

	model_config = {     #この3行は固定。
		"json_schema_extra": {
			"examples": [
				{
					"nextPage": 1,
					"data": [
						{
							"id": 10, "name": "平安鐘", "category": "公共藝術",
	                        "description": "平安鐘祈求大家的平安，這是為了紀念 921 地震週年的設計",
						    "address": " 臺北市大安區忠孝東路 4 段 1 號",
						    "transport": "公車：204、212、212直", "mrt": "忠孝復興",
						    "lat": 25.04181, "lng": 121.544814,
						    "images" :["http://140.112.3.4/images/92-0.jpg"]
						}
					]
				}
			]
		}
	}

class OneAttractioinSchema(pydantic.BaseModel):   #Pydanticでは、フィールドに初期値を設定しない場合、そのフィールドは必須と見な
	data: AttractionSchema    #デフォルト値として空のリストを設定。各インスタンスが独自のリストを持つように。＝[]だと各自共通に

	model_config = {
		"json_schema_extra": {
			"examples": [
				{
					"data":
						{
							"id": 10, "name": "平安鐘", "category": "公共藝術",
							"description": "平安鐘祈求大家的平安，這是為了紀念 921 地震週年的設計",
							"address": " 臺北市大安區忠孝東路 4 段 1 號",
							"transport": "公車：204、212、212直", "mrt": "忠孝復興",
							"lat": 25.04181, "lng": 121.544814,
							"images" :["http://140.112.3.4/images/92-0.jpg"]
						}
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


AttractionRouter = fastapi.APIRouter()


@AttractionRouter.get("/api/attractions",
	response_model = typing.Union[AllAttractionSchema, ErrorResponseSchema],
	responses = {
		200: {"model": AllAttractionSchema, "description": "正常運作"},
		500: {"model": ErrorResponseSchema, "description": "伺服器內部錯誤"}
	}) #...は必須。ge=より大きいgreater than。Optionalをつけることで、str又はNoneどちらかを受け取れる。defaultはNone, キーワードの最小長が1文字
async def get_all(
	page: int = fastapi.Query(..., ge = 0, description = "要取得的分頁，每頁 12 筆資料"),
	keyword: typing.Optional[str] = fastapi.Query(
		None,
		min_length = 1,
	    description = "用來完全比對捷運站名稱、或模糊比對景點名稱的關鍵字，沒有給定則不做篩選"
)):
	size = 12
	attractions = AttractionModel.get_all(size, page, keyword)
	next_page = page + 1 if len(attractions) == size else None
	return AttractionView.render_all(next_page, attractions)


@AttractionRouter.get("/api/attraction/{attractionId}",
	response_model = typing.Union[AllAttractionSchema, ErrorResponseSchema],
    responses = {
        200: {"model": AllAttractionSchema, "description": "景點資料"},
        400: {"model": ErrorResponseSchema, "description": "景點編號不正確"},
        500: {"model": ErrorResponseSchema, "description": "伺服器內部錯誤"}
    })
async def get_detail(attractionId: int = fastapi.Path(description = "景點編號")):
	attraction = AttractionModel.get_detail(attractionId)
	return AttractionView.render_detail(attraction)