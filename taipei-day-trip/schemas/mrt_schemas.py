#Standard Lib
import typing   #Optional(値が指定された型または、Noneを受け入れるのに必要), List(list内の要素の型を指定するために使用), Union(2つの結合)

#3rd-party Lib
import pydantic #BaseModel, Field(default値などの設定)


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