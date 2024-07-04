# 例外処理はアプリケーションのロジックの一部であり、設定（config）とは性質が異なる故単独dirが必要。
#Standard Lib
import fastapi   #Request, HTTPException

#Local Lib
from config.log_config import logger
from schemas.common_schemas import ResErrorSchema


#グローバルエラーハンドラーを設定することで、個々のエンドポイントでtry-except文を使用する必要がなくなる。
class LoggerCritical(Exception):     #オリジナルの例外
    def __init__(self, message = "重大Error"):
        self.message = message
        super().__init__(self.message)


async def critical_err_handler(request: fastapi.Request, exc: LoggerCritical): #内部＋外部(簡易)Error  #excには例外の『インスタンス＝Obj』が自動で渡される(外見はメッセージ文だが、型はObj)
    logger.critical(
        f"==== Critical例外處理\n"
        f"==== except的e訊息 ==== {str(exc.__cause__)}\n"
        f"==== raise的e訊息 ==== {str(exc)}\n"
    ) #exc.__cause__はfrom eのe。エラーメッセをcatch, str無くても表せるが、excはあくまでもobjなので、strを使った方が適切。
    return fastapi.responses.JSONResponse(
        status_code = 500,  #contentで無いため表示されない
        content = {"error": True, "message": "伺服器內部錯誤 Internal Server Error"}
    )
    # return ResErrorSchema(
    #     error = True,
    #     message ="伺服器內部錯誤 Internal Server Error",
    #     status_code = 500
    # )  #defaultで500番を返す


async def http_err_handler(request: fastapi.Request, exc: fastapi.HTTPException):  #内部＋外部(詳細)Error, クライアントに詳細を返す際に使用
    logger.error(
        f"==== HTTP例外處理\n"
        f"==== except的e訊息 ==== {exc.detail}\n"
        f"==== raise的e訊息 ==== {exc.status_code}\n"
    )
    return fastapi.responses.JSONResponse(   #swaggerUIにはstatus_codeが含まれていない為、pydanticが使えなく、JsonResponseを使う
        status_code = exc.status_code,
        content = {"error": True, "message": exc.detail}
    )
    # return ResErrorSchema(
    #     error = True,
    #     message = exc.detail,
    #     status_code = exc.status_code #固定値でなくclientに合わせたstatus_codeを返す(これがないと200を返す)
    # )


async def global_err_handler(request: fastapi.Request, exc: Exception):   #全てのEndポイントで発生する未処理の例外をキャッチ(raise無しのerr, try囲んでなくてもキャッチ)
    logger.error(
        f"==== Global例外處理\n"
        f"==== except的e訊息 ==== {str(exc.__cause__)}\n"
        f"==== raise的e訊息 ==== {str(exc)}\n"
    )
    return fastapi.responses.JSONResponse(
        status_code = 500,
        content = {"error": True, "message": "伺服器內部錯誤 Internal Server Error"}
    )
    # return ResErrorSchema(
    #     error = True,
    #     message ="伺服器內部錯誤 Internal Server Error",
    #     status_code = 500
    # )  #defaultで500番を返す