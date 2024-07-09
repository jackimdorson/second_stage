#3rd-party Lib
import pydantic #BaseModel, Field(default値などの設定)


class ResErrorSchema(pydantic.BaseModel):
    error: bool
    message: str
    status_code: int = pydantic.Field(exclude = True)  #swaggerUIで非表示にする記述

    class Config:     #舊一點的寫法
        json_schema_extra = {  #json_schema_extra可顯示字, schema_extra只能顯示dataType, 故採取前者
            "examples": [
                {
                    "error": True,
                    "message": "請按照情境提供對應的錯誤訊息"
                }
            ]
        }


class ResOkSchema(pydantic.BaseModel):
	ok: bool

	model_config = {
		"json_schema_extra": {
			"examples": [
				{
					"ok": True
				}
			]
		}
	}