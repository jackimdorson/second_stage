#Standard Lib
import datetime
import fastapi

#Local Lib
from schemas.common_schemas import ResOkSchema
from schemas.shopping_schemas import GetBooking200Schema, BaseBookingAttractionSchema, GetCart200Child1Schema, GetCart200Schema, PostOrders200Schema, GetOrderNum200Schema, GetOrderNum200Child1Schema, PostOrdersReqChild2Schema, BaseContactSchema


#booking_Endpoint
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


#order_Endpoint
class OrderView:
    @staticmethod
    def return_200(order_number: int) -> PostOrders200Schema:
        return PostOrders200Schema(
            data = {
                "number": order_number,
                "payment": {
                    "status": 0,
                    "message": "付款成功"
                }
            }
        )


    @staticmethod
    def return_200_get_order_number(fetchone) -> GetOrderNum200Schema:
        status, price, order_num, phone, date, time, a_id, a_name, a_address, name, mail, img = fetchone.values()
        date_str = date.isoformat() if isinstance(date, datetime.date) else str(date)  # 日付(date)は直接渡せないので、文字列に一度変換してから渡す(もし文字列ならそのまま使用)

        return GetOrderNum200Schema(data = GetOrderNum200Child1Schema(
                price = price,
                trip = PostOrdersReqChild2Schema(
                    attraction = BaseBookingAttractionSchema(
                        id = a_id, name = a_name, address = a_address, image = img
                    ), date = date_str, time = time
                ), contact = BaseContactSchema(
                    name = name, email = mail, phone = phone
            ), number = order_num, status = status,
        ))


    @staticmethod
    def raise_400():
        raise fastapi.HTTPException(status_code = 400, detail = "訂單建立失敗，輸入不正確或其他原因")


    @staticmethod
    def raise_403():
        raise fastapi.HTTPException(status_code = 403, detail = "未登入系統, 拒絕存取")
