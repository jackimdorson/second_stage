#Local Lib
from schemas.attraction_schemas import BaseAttractionSchema, GetAttractions200Schema, GetAttractionId200Schema


class AttractionView:
    @staticmethod
    def render_all(next_page: int | None, attractions: list[BaseAttractionSchema]) -> GetAttractions200Schema:
        return GetAttractions200Schema(nextPage = next_page, data = attractions)


    @staticmethod
    def render_detail(attraction: dict) -> GetAttractionId200Schema:
        return GetAttractionId200Schema(data = attraction)