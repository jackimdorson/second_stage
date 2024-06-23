import fastapi


class AttractionView:
    def render_all(next_page, attractions):
        if not attractions:
            raise fastapi.HTTPException(
                status_code = 404,
                detail = {"error": True, "message": "無資料"}
            )
        return fastapi.responses.JSONResponse(
            content = fastapi.encoders.jsonable_encoder(
                {"nextPage": next_page, "data": attractions}),
			headers = {"Content-Type": "application/json; charset=utf-8"})


    def render_detail(attraction):
        if not attraction:
            raise fastapi.HTTPException(
                status_code = 400,
                detail = {"error": True, "message": "景點編號不正確, 無資料"}
            )
        return fastapi.responses.JSONResponse(
            content = fastapi.encoders.jsonable_encoder({"data": attraction}),
			headers = {"Content-Type": "application/json; charset=utf-8"})