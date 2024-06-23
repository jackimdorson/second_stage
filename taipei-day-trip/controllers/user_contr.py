from models.user_model import UserModel
from views.user_view import UserView
import fastapi
import pydantic
import typing


class UserSchema(pydantic.BaseModel):
	id: int
	name: str
	email: str

class JwtSchema(pydantic.BaseModel):
	data: UserSchema

	model_config = {
		"json_schema_extra": {
			"examples": [
				{
                    "data": {
                        "id": 1,
                        "name": "彭彭彭",
                        "email": "ply@ply.com"
					}
				}
			]
		}
	}

class JwtRequestSchema(pydantic.BaseModel):
	email: str
	password: str

	model_config = {
		"json_schema_extra": {
			"examples": [
				{
					"email": "ply@ply.com",
                    "password": "12345678"
				}
			]
		}
	}

class SignUpRequestSchema(pydantic.BaseModel):
	name: str
	email: str
	password: str

	model_config = {
		"json_schema_extra": {
			"examples": [
				{
					"name": "彭彭彭",
  					"email": "ply@ply.com",
  					"password": "12345678"
				}
			]
		}
	}

class JwtOkResponseSchema(pydantic.BaseModel):
	token: str

	model_config = {
		"json_schema_extra": {
			"examples": [
				{
					"token": "a21312xzDSADAsadasd8u32klKDFuSAD"
				}
			]
		}
	}

class OkResponseSchema(pydantic.BaseModel):
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

class ErrorResponseSchema(pydantic.BaseModel):
    error: bool
    message: str

    class Config:  #舊一點的寫法
        json_schema_extra = {
            "examples": [
                {
                    "error": True,
                    "message": "請按照情境提供對應的錯誤訊息"
                }
            ]
        }


UserRouter = fastapi.APIRouter()


@UserRouter.post("/api/user",
	response_model = typing.Union[OkResponseSchema, ErrorResponseSchema],
    responses = {
        200: {"model": OkResponseSchema, "description": "註冊成功"},
        400: {"model": ErrorResponseSchema, "description": "註冊失敗, 重複的Email或其他原因"},
        500: {"model": ErrorResponseSchema, "description": "伺服器內部錯誤"}
    })
async def create_account(user: SignUpRequestSchema):
    tf_response = UserModel.create_account(user)
    return UserView.render_account(tf_response)


@UserRouter.get("/api/user/auth",  # JWTの検証
	response_model = JwtSchema,
	responses = {
		200: {"model": JwtSchema, "description": "已登入的會員資料, null 表示未登入"}
	})  #Header＝RequestHeaderからautho..を取得(defaultでは全て小文字に変換される故注意)なければNoneを返す
async def get_user_info(authorization: str = fastapi.Header(None)):
	decoded_token = UserModel.get_user_info(authorization)
	return UserView.render_user_info(decoded_token)


@UserRouter.put("/api/user/auth",  #登入成功即生產JWT
	response_model = typing.Union[JwtOkResponseSchema, ErrorResponseSchema],
	responses = {
        200: {"model": JwtOkResponseSchema, "description": "登入成功，取得有效期為七天的 JWT 加密字串"},
        400: {"model": ErrorResponseSchema, "description": "登入失敗，帳號或密碼錯誤或其他原因"},
        500: {"model": ErrorResponseSchema, "description": "伺服器內部錯誤"}
    })
async def get_jwt(auth: JwtRequestSchema):
	encoded_token = UserModel.get_jwt(auth)
	return UserView.render_jwt(encoded_token)