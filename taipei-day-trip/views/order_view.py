import fastapi
from schemas.order_schemas import PostOrders200Schema


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
    def raise_400():
        raise fastapi.HTTPException(status_code = 400, detail = "訂單建立失敗，輸入不正確或其他原因")


    @staticmethod
    def raise_403():
        raise fastapi.HTTPException(status_code = 403, detail = "未登入系統, 拒絕存取")
