#Local Lib
from schemas.mrt_schemas import GetMrts200Schema


class MrtView:
    @staticmethod
    def render_mrt_list(mrt_list: list[str]) -> GetMrts200Schema:
        return GetMrts200Schema(data = mrt_list)   #dataはpydanticのGetMrts200Schemaに定義されている。