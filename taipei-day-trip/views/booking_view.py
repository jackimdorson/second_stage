from schemas.common_schemas import ResOkSchema
from schemas.booking_schemas import ReqBookingSchema, ReqCartSchema, AttractionItemSchema
import fastapi
import datetime

class BookingView:
    def render_detail(newest_item) -> ReqCartSchema:
        if newest_item is None:
            return ReqCartSchema(data = None)
        date_obj, time, price, id, name, address , img_url = newest_item.values()
        # 日付(date)は直接渡せないので、文字列に一度変換してから渡す(もし文字列ならそのまま使用)
        date_str = date_obj.isoformat() if isinstance(date_obj, datetime.date) else str(date_obj)

        return fastapi.responses.JSONResponse(
            content = {
                "data": {
                    "attraction": {
                        "id": id, "name": name, "address": address, "image": img_url
                    },
                    "date": date_str, "time": time, "price": price
                }
            }
        )


    def render_is_success(is_success: bool) -> ResOkSchema:
        if not is_success:
            raise fastapi.HTTPException(
                status_code = 400,
                detail = "註冊失敗, 重複的Email或其他原因"
            )
        return ResOkSchema(ok = True)
        # return fastapi.responses.JSONResponse(
        #     content = {"ok": True},
        #     headers = {"Content-Type": "application/json; charset=utf-8"})
