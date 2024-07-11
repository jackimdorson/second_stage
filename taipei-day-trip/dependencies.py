#再利用性が高い場合にDependsを使う。依存関係関数で例外が発生した場合、エンドポイント関数は呼び出されない。

# Standard Lib
import fastapi

#Local Lib
from schemas.user_schemas import GetAuth200Schema
from models.auth_model import UserModel
from views.auth_view import UserView



async def has_jwt_or_null(authorization: str | None = fastapi.Header(None)): #必ずauthorization
    if (authorization is None):  #Noneの場合のEarly Return
        return GetAuth200Schema(data = None)

    decoded_token = UserModel.get_user_info(authorization)

    if (not decoded_token):  #改ざんされた場合
        return GetAuth200Schema(data = None)
    return UserView.render_user_info(decoded_token)



async def has_jwt_or_error(authorization: str | None = fastapi.Header(None)): #Noneで受ければHttpExceptionでエラーを返せる
    if (authorization is None):  #Noneの場合のEarly Return
        raise fastapi.HTTPException(status_code = 403, detail = "未登入系統，拒絕存取")

    decoded_jwt = UserModel.get_user_info(authorization)

    if (not decoded_jwt):  #改ざんされた場合
        raise fastapi.HTTPException(status_code = 403, detail = "未登入系統，拒絕存取")
    return UserView.render_user_info(decoded_jwt)



async def attraction_query_param():
    pass