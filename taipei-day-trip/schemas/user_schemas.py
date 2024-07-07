#3rd-party Lib
import pydantic


class BaseUserInfoSchema(pydantic.BaseModel):
	id: int
	name: str
	email: pydantic.EmailStr   #有効なメールアドレス形式


class BaseSignInSchema(pydantic.BaseModel):
	email: pydantic.EmailStr
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


class BaseSignUpSchema(BaseSignInSchema):
	name: str

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


class BaseTokenStrSchema(pydantic.BaseModel):
	token: str #SecretStrにすることで、機密情報へのアクセス(get_secret_value())が意図的か判別可能に

	model_config = {
		"json_schema_extra": {
			"examples": [
				{
					"token": "a21312xzDSADAsadasd8u32klKDFuSAD"
				}
			]
		}
	}


class GetAuth200Schema(pydantic.BaseModel):
	data: BaseUserInfoSchema | None

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