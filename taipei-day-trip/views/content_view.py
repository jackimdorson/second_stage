#Local Lib
from schemas.content_schemas import BaseAttractionSchema, GetAttractions200Schema, GetAttractionId200Schema, GetMrts200Schema


class AttractionView:
    @staticmethod
    def render_all(next_page: int | None, attractions: list[BaseAttractionSchema]) -> GetAttractions200Schema:
        return GetAttractions200Schema(nextPage = next_page, data = attractions)


    @staticmethod
    def render_detail(attraction: dict) -> GetAttractionId200Schema:
        return GetAttractionId200Schema(data = attraction)


class MrtView:
    @staticmethod
    def render_mrt_list(mrt_list: list[str]) -> GetMrts200Schema:
        return GetMrts200Schema(data = mrt_list)   #dataはpydanticのGetMrts200Schemaに定義されている。