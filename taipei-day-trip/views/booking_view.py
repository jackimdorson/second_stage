from schemas.common_schemas import ResOkSchema
from schemas.booking_schemas import ReqCartSchema, AttractionItemSchema, cartItemSchema
import datetime

class BookingView:
    @staticmethod
    def render_detail(newest_item: dict) -> ReqCartSchema:
        date_obj, time, price, id, name, address , img_url = newest_item.values()
        date_str = date_obj.isoformat() if isinstance(date_obj, datetime.date) else str(date_obj)  # 日付(date)は直接渡せないので、文字列に一度変換してから渡す(もし文字列ならそのまま使用)

        return ReqCartSchema(data = cartItemSchema(
            attraction = AttractionItemSchema(id = id, name = name, address = address, image = img_url),
            date = date_str, time = time, price = price))


    @staticmethod
    def render_is_success(is_success: bool) -> ResOkSchema:
        return ResOkSchema(ok = True)
