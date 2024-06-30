import pydantic


class UserItemSchema(pydantic.BaseModel):
	id: int
	name: str
	email: pydantic.EmailStr   #有効なメールアドレス形式


class ResUserInfoSchema(pydantic.BaseModel):
	data: UserItemSchema | None

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


class ReqSignUpSchema(pydantic.BaseModel):
	name: str
	email: pydantic.EmailStr
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


class ReqSignInSchema(pydantic.BaseModel):
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


class ResJwtSchema(pydantic.BaseModel):
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