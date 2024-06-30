import pydantic
import typing
import decimal  #Decimal(dbの型で, pyには無いためimportが必要)


class AttractionItemSchema(pydantic.BaseModel):  #pydanticの注意点：1.定義の順番、2.dbとの名称一致(asで取得)、3.データ型    dbの構造とは直接関係なく、APIの要件を満たすためのデータ構造を定義するためのもの=データの形式とバリデーションをを行う
	id: int
	name: str
	category: str
	description: str
	address: str
	transport: str
	mrt: str
	lat: decimal.Decimal
	lng: decimal.Decimal
	images: list[str]


class ResAllAttractionSchema(pydantic.BaseModel):
	nextPage: int | None = pydantic.Field(
		default = None, ge = 0,
		description = "下一頁的編號。若沒有下一頁,則為null"
	) #このフィールドは整数型で、値が存在しない場合はNoneを許容. デフォルト値をNoneに設定し、フィールドの説明を追加
	data: list[AttractionItemSchema] = pydantic.Field(default_factory = list) #listはmutableな為全てのインスタンスで共有されるのを防ぐ為、都度default値を生成する、default_factoryを使う。

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


class ResDetailAttractionSchema(pydantic.BaseModel):   #Pydanticでは、フィールドに初期値を設定しない場合、そのフィールドは必須と見な
	data: AttractionItemSchema    #デフォルト値として空のリストを設定。各インスタンスが独自のリストを持つように。＝[]だと各自共通に

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