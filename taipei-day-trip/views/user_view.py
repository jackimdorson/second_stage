import fastapi


class UserView:
    def render_account(tf_response):
        if not tf_response:
            raise fastapi.HTTPException(
                status_code = 400,
                detail = {"error": True, "message": "已被註冊過的Email"}
            )
        return fastapi.responses.JSONResponse(
            content = {"ok": True},
            headers = {"Content-Type": "application/json; charset=utf-8"})


    def render_user_info(decoded_token):
        if not decoded_token:
            return fastapi.responses.JSONResponse(
                content = {"data": None},
                headers = {"Content-Type": "application/json; charset=utf-8"}
            )
        user_id, user_name, email, iat, exp = decoded_token.values()
        return fastapi.responses.JSONResponse(
            content = {
                "data": {
                    "id": user_id, "name": user_name, "email": email
                }},
            headers = {"Content-Type": "application/json; charset=utf-8"})


    def render_jwt(encoded_token):
        if not encoded_token:
            raise fastapi.HTTPException(
                status_code = 400,
                detail = {"error": True, "message": "帳號或密碼輸入錯誤"}
            )
        return fastapi.responses.JSONResponse(
            content = {"token": encoded_token},
            headers = {"Content-Type": "application/json; charset=utf-8"})