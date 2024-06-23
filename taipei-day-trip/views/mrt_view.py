import fastapi


class MrtView:
    def render_mrt_list(mrt_list):
        if not mrt_list:
            raise Exception("db出問題:發生地=def get_mrt_list-2")
        return fastapi.responses.JSONResponse(
            content={"data": mrt_list},
            headers={"Content-Type": "application/json; charset=utf-8"})