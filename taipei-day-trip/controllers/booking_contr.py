from schemas.common_schemas import ResErrorSchema, ResOkSchema
from schemas.booking_schemas import ReqBookingSchema, ReqCartSchema
from models.booking_model import BookingModel
from views.booking_view import BookingView
import fastapi
import typing


BookingRouter = fastapi.APIRouter()


@BookingRouter.get("/api/booking",
    tags = ["Booking"],
    summary = "取得尚未確認下單的預定行程",
    response_model = typing.Union[ReqCartSchema, ResErrorSchema],
    responses = {
        200: {"model": ReqCartSchema, "description": "尚未確認下單的預定行程資料，null 表示沒有資料"},
        403: {"model": ResErrorSchema, "description": "未登入系統，拒絕存取"}
    })
async def get_booking_info(authorization: str | None = fastapi.Header(None)) -> ReqCartSchema: #名前衝突する為jwtと命名付けしない
    newest_item = BookingModel.get_booking_info(authorization)
    print(newest_item)
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
async def post_booking_info(cart_info: ReqBookingSchema) -> ResOkSchema:
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
async def delete_booking_info(authorization: str | None = fastapi.Header(None)) -> ResOkSchema | None: #Noneが帰る可能性がある為。
    is_success = BookingModel.delete_booking_info(authorization)
    return BookingView.render_is_success(is_success)