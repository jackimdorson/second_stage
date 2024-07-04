#Local Lib
from schemas.attraction_schemas import AttractionItemSchema, ResAllAttractionSchema, ResDetailAttractionSchema


class AttractionView:
    @staticmethod
    def render_all(next_page: int | None, attractions: list[AttractionItemSchema]) -> ResAllAttractionSchema:
        return ResAllAttractionSchema(nextPage = next_page, data = attractions)


    @staticmethod
    def render_detail(attraction: dict) -> ResDetailAttractionSchema:
        return ResDetailAttractionSchema(data = attraction)