from schemas.common_schemas import ResOkSchema
from schemas.user_schemas import UserItemSchema, ResUserInfoSchema, ResJwtSchema
import fastapi


class UserView:
    def render_account(tf_response: bool) -> ResOkSchema:
        if not tf_response:
            raise fastapi.HTTPException(
                status_code = 400,
                detail = "註冊失敗, 重複的Email或其他原因"
            )
        return ResOkSchema(ok = True)
        # return fastapi.responses.JSONResponse(
        #     content = {"ok": True},
        #     headers = {"Content-Type": "application/json; charset=utf-8"})


    def render_user_info(decoded_token) -> ResUserInfoSchema:
        if decoded_token is None:
            return ResUserInfoSchema(data = None)
            # return fastapi.responses.JSONResponse(
            #     content = {"data": None},
            #     headers = {"Content-Type": "application/json; charset=utf-8"}
            # )
        user_id, user_name, email, iat, exp = decoded_token.values()
        return ResUserInfoSchema(data = UserItemSchema(id = user_id, name = user_name, email = email))
        # return fastapi.responses.JSONResponse(
        #     content = {
        #         "data": {
        #             "id": user_id, "name": user_name, "email": email
        #         }},
        #     headers = {"Content-Type": "application/json; charset=utf-8"})


    def render_jwt(encoded_token) -> ResJwtSchema:
        if not encoded_token:
            raise fastapi.HTTPException(
                status_code = 400,
                detail = "帳號或密碼輸入錯誤"
            )
        return ResJwtSchema(token = encoded_token)
        # return fastapi.responses.JSONResponse(
        #     content = {"token": encoded_token},
        #     headers = {"Content-Type": "application/json; charset=utf-8"})