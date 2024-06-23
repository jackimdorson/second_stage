import logging
import fastapi  #Request, HTTPException


def setup_logger():
    logger = logging.getLogger('my_logger')   # ロガーの作成
    logger.setLevel(logging.DEBUG)    # ログレベルを設定, DEBUGレベル以上の全てのログメッセージが記録される
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')   # フォーマッターの作成(logメッセージのフォーマットasctime=TimeStamp, name=LoggerName, levelname=LogLevel)

    console_handler = logging.StreamHandler()   # コンソールハンドラーの作成
    console_handler.setLevel(logging.DEBUG)     # コンソールのログレベルを設定
    console_handler.setFormatter(formatter)     # フォーマッターを設定

    file_handler = logging.FileHandler('app.log')  #ファイルハンドラーの作成
    file_handler.setLevel(logging.DEBUG)           #ファイルのログレベルを設定
    file_handler.setFormatter(formatter)           #フォーマッターを設定

    logger.addHandler(console_handler)  #ロガーにハンドラーを追加
    logger.addHandler(file_handler)     #ログmsgの出力　
    return logger         #logger.debug('詳細なデバッグ情報') logger.info('一般的な情報')
    #logger.warning('警告msg')　logger.error('エラーmsg')　logger.critical('重大なmsg')


logger = setup_logger()


class LoggerCritical(Exception):     #オリジナルの例外
    def __init__(self, message = "重大Error"):
        self.message = message
        super().__init__(self.message)


async def critical_err_handler(request: fastapi.Request, exc: LoggerCritical): #内部＋外部(簡易)Error  #excには例外の『インスタンス＝Obj』が自動で渡される(外見はメッセージ文だが、型はObj)
    logger.critical(f"critical_exc===={str(exc.__cause__)}===={str(exc)}") #exc.__cause__はfrom eのe。エラーメッセをcatch, str無くても表せるが、excはあくまでもobjなので、strを使った方が適切。
    return fastapi.responses.JSONResponse(
        status_code = 500,  #contentで無いため表示されない
        content = {"error": True, "message": "伺服器內部錯誤 Internal Server Error"}
    )


async def http_err_handler(request: fastapi.Request, exc: fastapi.HTTPException):  #内部＋外部(詳細)Error, クライアントに詳細を返す際に使用
    logger.error(f"http_exc===={exc.detail}===={exc.status_code}")
    return fastapi.responses.JSONResponse(     #既にstatus_code = 400とdetailを返しているため不要
        content = exc.detail
    )


async def global_err_handler(request: fastapi.Request, exc: Exception):   #全てのEndポイントで発生する未処理の例外をキャッチ(raise無しのerr, try囲んでなくてもキャッチ)
    logger.error(f"global_exc===={str(exc.__cause__)}===={str(exc)}")
    return fastapi.responses.JSONResponse(
        status_code = 500,
        content = {"error": True, "message": "伺服器內部錯誤 Internal Server Error"}
    )