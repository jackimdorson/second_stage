from schemas.common_schemas import ResOkSchema
from schemas.user_schemas import UserItemSchema, ResUserInfoSchema, ResJwtSchema


class UserView:
    @staticmethod
    def render_account(tf_response: bool) -> ResOkSchema:
        return ResOkSchema(ok = True)


    @staticmethod
    def render_user_info(decoded_token) -> ResUserInfoSchema:
        user_id, user_name, email, iat, exp = decoded_token.values()
        return ResUserInfoSchema(data = UserItemSchema(id = user_id, name = user_name, email = email))


    @staticmethod
    def render_jwt(encoded_token) -> ResJwtSchema:
        return ResJwtSchema(token = encoded_token)