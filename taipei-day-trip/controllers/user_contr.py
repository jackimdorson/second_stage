from schemas.common_schemas import ResErrorSchema, ResOkSchema
from schemas.user_schemas import ResUserInfoSchema, ReqSignUpSchema, ReqSignInSchema, ResJwtSchema
from models.user_model import UserModel
from views.user_view import UserView
import fastapi
import typing


UserRouter = fastapi.APIRouter()


@UserRouter.post("/api/user",
	tags = ["User"],
    summary = "註冊一個新的會員",
	response_model = typing.Union[ResOkSchema, ResErrorSchema],
    responses = {
        200: {"model": ResOkSchema, "description": "註冊成功"},
        400: {"model": ResErrorSchema, "description": "註冊失敗, 重複的Email或其他原因"},
        500: {"model": ResErrorSchema, "description": "伺服器內部錯誤"}
    })
async def create_account(user: ReqSignUpSchema) -> ResOkSchema:
	tf_response = UserModel.create_account(user)
	if not tf_response:
		raise fastapi.HTTPException(status_code = 400, detail = "註冊失敗, 重複的Email或其他原因")
	return UserView.render_account(tf_response)


@UserRouter.get("/api/user/auth",  # JWTの検証
	tags = ["User"],
    summary = "取得當前登入的會員資訊",
	response_model = ResUserInfoSchema,
	responses = {
		200: {"model": ResUserInfoSchema, "description": "已登入的會員資料, null 表示未登入"}
	})  #Header＝RequestHeaderから"authorization"を取得(defaultでは全て小文字に変換される故注意)なければNoneを取得
async def get_user_info(authorization: str | None = fastapi.Header(None)) -> ResUserInfoSchema:  #名前衝突する為jwtと命名付けしない
	if (authorization is None):
		return ResUserInfoSchema(data = None)

	decoded_token = UserModel.get_user_info(authorization)

	if (not decoded_token):
		return ResUserInfoSchema(data = None)
	return UserView.render_user_info(decoded_token)


@UserRouter.put("/api/user/auth",  #登入成功即生產JWT
	tags = ["User"],
    summary = "登入會員帳戶",
	response_model = typing.Union[ResJwtSchema, ResErrorSchema],
	responses = {
        200: {"model": ResJwtSchema, "description": "登入成功，取得有效期為七天的 JWT 加密字串"},
        400: {"model": ResErrorSchema, "description": "登入失敗，帳號或密碼錯誤或其他原因"},
        500: {"model": ResErrorSchema, "description": "伺服器內部錯誤"}
    })
async def get_jwt(signin: ReqSignInSchema) -> ResJwtSchema:
	encoded_token = UserModel.get_jwt(signin)
	if not encoded_token:
		raise fastapi.HTTPException(status_code = 400, detail = "帳號或密碼輸入錯誤")
	return UserView.render_jwt(encoded_token)