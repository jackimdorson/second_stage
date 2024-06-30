from schemas.mrt_schemas import MrtListSchema
import typing


class MrtView:
    @staticmethod
    def render_mrt_list(mrt_list: typing.List[str]) -> MrtListSchema:
        # if not mrt_list:
        #     raise Exception("db出問題:發生地=def get_mrt_list-2")
        return MrtListSchema(data = mrt_list)   #dataはpydanticのMrtListSchemaに定義されている。

        # return fastapi.responses.JSONResponse(
        #     content={"data": mrt_list},
        #     headers={"Content-Type": "application/json; charset=utf-8"})