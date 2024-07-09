# 例外処理はアプリケーションのロジックの一部であり、設定（config）とは性質が異なる故単独dirが必要。
#Standard Lib
import fastapi   #Request, HTTPException
# import fastapi.exceptions

#Local Lib
from config.log_config import logger
from schemas.common_schemas import ResErrorSchema


#グローバルエラーハンドラーを設定することで、個々のエンドポイントでtry-except文を使用する必要がなくなる。
class LoggerCritical(Exception):     #オリジナルの例外
    def __init__(self, message = "重大Error"):
        self.message = message
        super().__init__(self.message)  #親クラスの初期化処理を行い、引数にmsgを付与


# 例外ハンドラは、リクエストObj(header,body,paramを格納)と例外Objの2つのパラメータを受け取る必要がある
async def critical_err_handler(_: fastapi.Request, exc: LoggerCritical): #内部＋外部(簡易)Error  #excには例外の『インスタンス＝Obj』が自動で渡される(外見はメッセージ文だが、型はObj)
    logger.critical(
        f"==== Global Critical  Exception\n"
        f"==== ①系統抓的(except as e) 出錯 ==== {str(exc.__cause__)}\n"
        f"==== ①自己弄的(raise from e) 出錯 ==== {str(exc)}\n"
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


async def http_err_handler(_: fastapi.Request, exc: fastapi.HTTPException):
    logger.error(
        f"==== Global HTTP Exception\n"
        f"==== 客戶端顯示 ==== {exc.status_code} {exc.detail}\n"
        f"==== ①沒錯 or ②系統抓的(except as e) 出錯 ==== {str(exc.__cause__) if exc.__cause__ else '沒錯'}\n"  #exc.__cause__.はexceptを使った際の、原因のエラーを指す。使わなければNoneが格納。
        f"==== ①沒錯 or ②自己弄的(raise from e) 出錯 ==== {str(exc) if exc else '沒錯'}\n"  #from eを使わない場合がある為唯一Noneがある
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



async def validation_err_handler(_: fastapi.Request, exc: fastapi.exceptions.RequestValidationError):  #requestは必須
    logger.error(
        f"==== Global Validation Exception\n"
        f"==== ①系統抓的 Error ==== {str(exc)}\n"    #validationはexceptを使うことが無い為exc.__cause__は不要。
        f"==== ①Error內容 ==== {str(exc.errors())}\n"  #validationエラーの詳細情報を含むリストを返す
    )
    return fastapi.responses.JSONResponse(
        status_code = 400,
        content = {"error": True, "message": "不接受的格式，請使用正確格式"}
    )



async def global_err_handler(_: fastapi.Request, exc: Exception):  #全ての未処理の例外をキャッチ(raise無しのerr, try囲んでなくてもキャッチ)
    logger.error(
        f"==== Global Exception\n"
        f"==== ①沒錯 or ②自己抓的 (except as e) 出錯 ==== {str(exc.__cause__) if exc.__cause__ else '沒錯'}\n"  #exc.__cause__.はexceptを使った際の、原因のエラーを指す。使わなければNoneが格納。
        f"==== ①系統抓的 or ②自己弄的 (raise from e) 出錯 ==== {str(exc)}\n"    #excは発生したError Obj(or exceptで発生させたエラー)を指す
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