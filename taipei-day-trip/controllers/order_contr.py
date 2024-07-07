#Standard Lib
import fastapi
import typing

#Local LIb
from schemas.common_schemas import ResErrorSchema
from schemas.order_schemas import PostOrdersReqSchema, PostOrders200Schema, GetOrderNum200Schema
from models.order_model import OrderModel
from views.order_view import OrderView


OrderRouter = fastapi.APIRouter()


@OrderRouter.post("/api/orders",
	tags = ["Order"],
	summary = "建立新的訂單, 並完成付款程序",
	response_model = typing.Union[PostOrders200Schema, ResErrorSchema],
	responses = {
        200: {"model": PostOrders200Schema, "description": "訂單建立成功，包含付款狀態 ( 可能成功或失敗 )"},
        400: {"model": ResErrorSchema, "description": "訂單建立失敗，輸入不正確或其他原因"},
		403: {"model": ResErrorSchema, "description": "未登入系統, 拒絕存取"},
        500: {"model": ResErrorSchema, "description": "伺服器內部錯誤"}
	})
async def post_orders(req_body: PostOrdersReqSchema, authorization: str | None = fastapi.Header(None)) -> PostOrders200Schema:
	if (authorization is None):
		OrderView.raise_403()
	order_number = await OrderModel.create_order(authorization, req_body)
	if (order_number is None):
		OrderView.raise_400()
	return OrderView.return_200(order_number)


@OrderRouter.get("/api/order/{orderNumber}",
	tags = ["Order"],
	summary = "建立新的訂單, 並完成付款程序",
	response_model = typing.Union[GetOrderNum200Schema, ResErrorSchema],
	responses = {
        200: {"model": GetOrderNum200Schema, "description": "根據訂單編號取得訂單資訊，null 表示沒有資料"},
        403: {"model": ResErrorSchema, "description": "未登入系統, 拒絕存取"}
    })
async def get_order_number(orderNumber: int = fastapi.Path(..., description = "訂單編號"), authorization: str | None = fastapi.Header(None)) -> GetOrderNum200Schema:
    print(orderNumber)
    if (authorization is None):
        OrderView.raise_403()
    fetchone = OrderModel.get_order_number(orderNumber)
    if (fetchone is None):
        return GetOrderNum200Schema(data = None)
    return OrderView.return_200_get_order_number(fetchone)