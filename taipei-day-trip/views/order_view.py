#Standard Lib
import datetime
import fastapi

#Local Lib
from schemas.order_schemas import PostOrders200Schema, GetOrderNum200Schema, GetOrderNum200Child1Schema, PostOrdersReqChild1Schema, PostOrdersReqChild2Schema, BaseBookingAttractionSchema, BaseContactSchema


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
