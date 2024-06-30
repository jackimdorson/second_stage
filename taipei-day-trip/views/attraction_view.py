from schemas.attraction_schemas import AttractionItemSchema, ResAllAttractionSchema, ResDetailAttractionSchema
import fastapi


class AttractionView:
    @staticmethod
    def render_all(next_page: int | None, attractions: list[AttractionItemSchema]) -> ResAllAttractionSchema:
        if not attractions:
            raise fastapi.HTTPException(
                status_code = 404,
                detail = "無資料"
            )
        else:
            return ResAllAttractionSchema(nextPage = next_page, data = attractions)
            
            # return fastapi.responses.JSONResponse(
            #     content = fastapi.encoders.jsonable_encoder(
            #         {"nextPage": next_page, "data": attractions}),
            #     headers = {"Content-Type": "application/json; charset=utf-8"})


    @staticmethod
    def render_detail(attraction: dict) -> ResDetailAttractionSchema:
        if not attraction:
            raise fastapi.HTTPException(
                status_code = 400,
                detail = "景點編號不正確, 無資料"
            )
        return ResDetailAttractionSchema(data = attraction)

        # return fastapi.responses.JSONResponse(
        #     content = fastapi.encoders.jsonable_encoder({"data": attraction}),
		# 	headers = {"Content-Type": "application/json; charset=utf-8"})