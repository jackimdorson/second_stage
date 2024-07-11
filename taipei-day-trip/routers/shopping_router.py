#Standard Lib
import fastapi
import typing

#3rd-party Lib
import pydantic

#Local Lib
from dependencies import has_jwt_or_error
from schemas.common_schemas import ResErrorSchema, ResOkSchema
from schemas.shopping_schemas import PostBookingReqSchema, GetBooking200Schema, GetCart200Schema, PostOrdersReqSchema, PostOrders200Schema, GetOrderNum200Schema
from models.shopping_model import BookingModel, OrderModel
from views.shopping_view import BookingView, OrderView



BookingRouter = fastapi.APIRouter(tags = ["Shopping"])
OrderRouter = fastapi.APIRouter(tags = ["Shopping"])



@BookingRouter.get("/api/booking",
    summary = "取得尚未確認下單的預定行程",
    response_model = typing.Union[GetBooking200Schema, ResErrorSchema],
    responses = {
        200: {"model": GetBooking200Schema, "description": "尚未確認下單的預定行程資料，null 表示沒有資料"}, #データありとnullのパターンがある
        403: {"model": ResErrorSchema, "description": "未登入系統，拒絕存取"}
    })
async def get_booking(decoded_jwt: str | None = fastapi.Depends(has_jwt_or_error)) -> GetBooking200Schema: #名前衝突する為jwtと命名付けしない
    newest_item = BookingModel.get_booking_info(decoded_jwt)
    if (newest_item is None):
        return GetBooking200Schema(data = None)   #要件定義に404がないため、200番で返すことに注意
    return BookingView.render_detail(newest_item)



@BookingRouter.post("/api/booking",
    summary = "建立新的預定行程",
    response_model = typing.Union[ResOkSchema, ResErrorSchema],
    responses = {
        200: {"model": ResOkSchema, "description": "建立成功"},
        400: {"model": ResErrorSchema, "description": "建立失敗，輸入不正確或其他原因"},
        403: {"model": ResErrorSchema, "description": "未登入系統，拒絕存取"},
        500: {"model": ResErrorSchema, "description": "伺服器內部錯誤"}
    })
async def post_booking(cart_info: PostBookingReqSchema, _: str | None = fastapi.Depends(has_jwt_or_error)) -> ResOkSchema: #_:返り値を使わないの明示
    is_success = BookingModel.post_booking_info(cart_info)
    return BookingView.render_is_success(is_success)



@BookingRouter.delete("/api/booking",
    summary = "刪除目前的預定行程",
    response_model = typing.Union[ResOkSchema, ResErrorSchema],
    responses = {
        200: {"model": ResOkSchema, "description": "刪除成功"},
        403: {"model": ResErrorSchema, "description": "未登入系統，拒絕存取"},
    })
async def delete_booking(decoded_jwt: str | None = fastapi.Depends(has_jwt_or_error)) -> ResOkSchema | None: #Noneが帰る可能性がある為。
    is_success = BookingModel.delete_booking_info(decoded_jwt)
    return BookingView.render_is_success(is_success)



# #########多種購物車
# @BookingRouter.get("/api/cart",
#     tags = ["Cart"],
#     summary = "取得尚未確認下單的預定行程",
#     response_model = typing.Union[GetBooking200Schema, ResErrorSchema],
#     responses = {
#         200: {"model": GetCart200Schema, "description": "尚未確認下單的預定行程資料，null 表示沒有資料"}, #データありとnullのパターンがある
#         403: {"model": ResErrorSchema, "description": "未登入系統，拒絕存取"}
#     })
# async def get_cart(auth: str | None = fastapi.Depends(has_jwt_or_error)) -> GetCart200Schema: #名前衝突する為jwtと命名付けしない
#     all_items = BookingModel.get_booking_info(auth)

#     if (all_items is None):
#         return GetBooking200Schema(data = None)   #要件定義に404がないため、200番で返すことに注意
#     return BookingView.render_all(all_items)


# @BookingRouter.delete("/api/cart",
#     tags = ["Cart"],
#     summary = "刪除目前的預定行程",
#     response_model = typing.Union[ResOkSchema, ResErrorSchema],
#     responses = {
#         200: {"model": ResOkSchema, "description": "刪除成功"},
#         403: {"model": ResErrorSchema, "description": "未登入系統，拒絕存取"},
#     })
# async def delete_cart(item_id: PostBookingReqSchema, auth: str | None = fastapi.Depends(has_jwt_or_error)) -> ResOkSchema | None: #Noneが帰る可能性がある為。
#     is_success = BookingModel.delete_cart_info(auth, item_id)
#     return BookingView.render_is_success(is_success)



#order_Endpoint
@OrderRouter.post("/api/orders",
	summary = "建立新的訂單, 並完成付款程序",
    description = "根據預定行程中的資料，建立新的訂單，並串接第三方金流，完成付款程序",
	response_model = typing.Union[PostOrders200Schema, ResErrorSchema],
	responses = {
        200: {"model": PostOrders200Schema, "description": "訂單建立成功，包含付款狀態 ( 可能成功或失敗 )"},
        400: {"model": ResErrorSchema, "description": "訂單建立失敗，輸入不正確或其他原因"},
		403: {"model": ResErrorSchema, "description": "未登入系統, 拒絕存取"},
        500: {"model": ResErrorSchema, "description": "伺服器內部錯誤"}
	})
async def post_orders(req_body: PostOrdersReqSchema, decoded_jwt: str | None = fastapi.Depends(has_jwt_or_error)) -> PostOrders200Schema:
	order_number = await OrderModel.create_order(decoded_jwt, req_body)
	if (order_number is None):
		OrderView.raise_400()
	return OrderView.return_200(order_number)



@OrderRouter.get("/api/order/{orderNumber}",
	summary = "根據訂單編號取得訂單資訊",
	response_model = typing.Union[GetOrderNum200Schema, ResErrorSchema],
	responses = {
        200: {"model": GetOrderNum200Schema, "description": "根據訂單編號取得訂單資訊，null 表示沒有資料"},
        403: {"model": ResErrorSchema, "description": "未登入系統, 拒絕存取"}
    }) #fastapi.Pathやfastapi.Queryは、主にパラメータの詳細な説明やバリデーションを追加したい場合に使用される。
async def get_order_number(orderNumber: int = fastapi.Path(description = "訂單編號"), _: str | None = fastapi.Depends(has_jwt_or_error)) -> GetOrderNum200Schema:
    fetchone = OrderModel.get_order_number(orderNumber)
    if (fetchone is None):
        return GetOrderNum200Schema(data = None)
    return OrderView.return_200_get_order_number(fetchone)