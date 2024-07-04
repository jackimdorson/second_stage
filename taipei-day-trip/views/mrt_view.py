#Local Lib
from schemas.mrt_schemas import MrtListSchema


class MrtView:
    @staticmethod
    def render_mrt_list(mrt_list: list[str]) -> MrtListSchema:
        return MrtListSchema(data = mrt_list)   #dataはpydanticのMrtListSchemaに定義されている。