#Standard Lib
import datetime

#Local Lib
from schemas.common_schemas import ResOkSchema
from schemas.booking_schemas import GetBooking200Schema, BaseBookingAttractionSchema, GetCart200Child1Schema, GetCart200Schema


class BookingView:
    @staticmethod
    def render_detail(newest_item: dict) -> GetBooking200Schema:
        date_obj, time, price, id, name, address , img_url = newest_item.values()
        date_str = date_obj.isoformat() if isinstance(date_obj, datetime.date) else str(date_obj)  # 日付(date)は直接渡せないので、文字列に一度変換してから渡す(もし文字列ならそのまま使用)

        return GetBooking200Schema(data = GetCart200Child1Schema(
            attraction = BaseBookingAttractionSchema(id = id, name = name, address = address, image = img_url),
            date = date_str, time = time, price = price))


    @staticmethod
    def render_is_success(is_success: bool) -> ResOkSchema:
        return ResOkSchema(ok = True)


#########多種購物車
    @staticmethod
    def render_all(all_items: list) -> GetCart200Schema:
        for item in all_items:   #fetchallのアンパッキング
            date_obj, time, price, id, name, address , img_url = item
            date_str = date_obj.isoformat() if isinstance(date_obj, datetime.date) else str(date_obj)  # 日付(date)は直接渡せないので、文字列に一度変換してから渡す(もし文字列ならそのまま使用)

        return GetCart200Schema(data = list[GetCart200Child1Schema](
            attraction = BaseBookingAttractionSchema(id = id, name = name, address = address, image = img_url),
            date = date_str, time = time, price = price))
