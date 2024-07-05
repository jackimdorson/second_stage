#Standard Lib
import fastapi
import typing

#3rd-party Lib
import pydantic

#Local Lib
from schemas.common_schemas import ResErrorSchema, ResOkSchema
from schemas.booking_schemas import PostBookingReqSchema, GetBooking200Schema, GetCart200Schema
from models.booking_model import BookingModel
from views.booking_view import BookingView


BookingRouter = fastapi.APIRouter()


@BookingRouter.get("/api/booking",
    tags = ["Booking"],
    summary = "取得尚未確認下單的預定行程",
    response_model = typing.Union[GetBooking200Schema, ResErrorSchema],
    responses = {
        200: {"model": GetBooking200Schema, "description": "尚未確認下單的預定行程資料，null 表示沒有資料"}, #データありとnullのパターンがある
        403: {"model": ResErrorSchema, "description": "未登入系統，拒絕存取"}
    })
async def get_booking(authorization: str | None = fastapi.Header(None)) -> GetBooking200Schema: #名前衝突する為jwtと命名付けしない
    if (authorization is None):
        raise fastapi.HTTPException(status_code = 403, detail = "未登入系統，拒絕存取") #viewではなく、検証のためコントローラーに記述

    newest_item = BookingModel.get_booking_info(authorization)

    if (newest_item is None):
        return GetBooking200Schema(data = None)   #要件定義に404がないため、200番で返すことに注意
    return BookingView.render_detail(newest_item)


@BookingRouter.post("/api/booking",
    tags = ["Booking"],
    summary = "建立新的預定行程",
    response_model = typing.Union[ResOkSchema, ResErrorSchema],
    responses = {
        200: {"model": ResOkSchema, "description": "建立成功"},
        400: {"model": ResErrorSchema, "description": "建立失敗，輸入不正確或其他原因"},
        403: {"model": ResErrorSchema, "description": "未登入系統，拒絕存取"},
        500: {"model": ResErrorSchema, "description": "伺服器內部錯誤"}
    })
async def post_booking(cart_info: PostBookingReqSchema, authorization: str | None = fastapi.Header(None)) -> ResOkSchema:
    if (authorization is None):
        raise fastapi.HTTPException(status_code = 403, detail = "未登入系統，拒絕存取") #viewではなく、検証のためコントローラーに記述

    try:
        cart_info = PostBookingReqSchema(**cart_info.model_dump())  #dictは非推奨必ずmodel_dumpを使う
    except pydantic.ValidationError:
        raise fastapi.HTTPException(status_code=400, detail = "建立失敗，輸入不正確或其他原因")

    is_success = BookingModel.post_booking_info(cart_info)
    return BookingView.render_is_success(is_success)


@BookingRouter.delete("/api/booking",
    tags = ["Booking"],
    summary = "刪除目前的預定行程",
    response_model = typing.Union[ResOkSchema, ResErrorSchema],
    responses = {
        200: {"model": ResOkSchema, "description": "刪除成功"},
        403: {"model": ResErrorSchema, "description": "未登入系統，拒絕存取"},
    })
async def delete_booking(authorization: str | None = fastapi.Header(None)) -> ResOkSchema | None: #Noneが帰る可能性がある為。
    if (authorization is None):
        raise fastapi.HTTPException(status_code = 403, detail = "未登入系統，拒絕存取")

    is_success = BookingModel.delete_booking_info(authorization)
    return BookingView.render_is_success(is_success)


#########多種購物車
@BookingRouter.get("/api/cart",
    tags = ["Cart"],
    summary = "取得尚未確認下單的預定行程",
    response_model = typing.Union[GetBooking200Schema, ResErrorSchema],
    responses = {
        200: {"model": GetCart200Schema, "description": "尚未確認下單的預定行程資料，null 表示沒有資料"}, #データありとnullのパターンがある
        403: {"model": ResErrorSchema, "description": "未登入系統，拒絕存取"}
    })
async def get_cart(authorization: str | None = fastapi.Header(None)) -> GetCart200Schema: #名前衝突する為jwtと命名付けしない
    if (authorization is None):
        raise fastapi.HTTPException(status_code = 403, detail = "未登入系統，拒絕存取") #viewではなく、検証のためコントローラーに記述

    all_items = BookingModel.get_booking_info(authorization)

    if (all_items is None):
        return GetBooking200Schema(data = None)   #要件定義に404がないため、200番で返すことに注意
    return BookingView.render_all(all_items)


@BookingRouter.delete("/api/cart",
    tags = ["Cart"],
    summary = "刪除目前的預定行程",
    response_model = typing.Union[ResOkSchema, ResErrorSchema],
    responses = {
        200: {"model": ResOkSchema, "description": "刪除成功"},
        403: {"model": ResErrorSchema, "description": "未登入系統，拒絕存取"},
    })
async def delete_cart(item_id: PostBookingReqSchema, authorization: str | None = fastapi.Header(None)) -> ResOkSchema | None: #Noneが帰る可能性がある為。
    if (authorization is None):
        raise fastapi.HTTPException(status_code = 403, detail = "未登入系統，拒絕存取")

    is_success = BookingModel.delete_cart_info(authorization, item_id)
    return BookingView.render_is_success(is_success)