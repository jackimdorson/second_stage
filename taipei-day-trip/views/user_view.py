#Local Lib
from schemas.common_schemas import ResOkSchema
from schemas.user_schemas import BaseUserInfoSchema, GetAuth200Schema, BaseTokenStrSchema


class UserView:
    @staticmethod
    def render_account(tf_response: bool) -> ResOkSchema:
        return ResOkSchema(ok = True)


    @staticmethod
    def render_user_info(decoded_token) -> GetAuth200Schema:
        user_id, user_name, email, iat, exp = decoded_token.values()
        return GetAuth200Schema(data = BaseUserInfoSchema(id = user_id, name = user_name, email = email))


    @staticmethod
    def render_jwt(encoded_token) -> BaseTokenStrSchema:
        return BaseTokenStrSchema(token = encoded_token)