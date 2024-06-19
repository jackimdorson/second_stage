from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os                          #環境変数(.env)の読み込みに必要
from dotenv import load_dotenv     #環境変数(.env)の読み込みに必要import json
import mysql.connector
import logging
from mysql.connector import pooling, Error   # Connection Poolの設定


def setup_logger():
    logger = logging.getLogger('my_logger')   # ロガーの作成
    logger.setLevel(logging.DEBUG)    # ログレベルを設定, DEBUGレベル以上の全てのログメッセージが記録される
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')   # フォーマッターの作成(logメッセージのフォーマットasctime=TimeStamp, name=LoggerName, levelname=LogLevel)

    console_handler = logging.StreamHandler()   # コンソールハンドラーの作成
    console_handler.setLevel(logging.DEBUG)     # コンソールのログレベルを設定
    console_handler.setFormatter(formatter)     # フォーマッターを設定

    file_handler = logging.FileHandler('app.log')  # ファイルハンドラーの作成
    file_handler.setLevel(logging.DEBUG)    # ファイルのログレベルを設定
    file_handler.setFormatter(formatter)    # フォーマッターを設定

    logger.addHandler(console_handler) # ロガーにハンドラーを追加
    logger.addHandler(file_handler)    #ログメッセージの出力　　# logger.debug('詳細なデバッグ情報')　　　# logger.info('一般的な情報')
    return logger
    # logger.warning('警告メッセージ')　　# logger.error('エラーメッセージ　')　　# logger.critical('重大なエラーメッセージ　')

logger = setup_logger()
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
load_dotenv()   # 環境変数の読み込み

private_key = os.getenv("PRIVATE_KEY").replace("\\n", "\n")   #秘密鍵を取得し、改行を適切に処理(秘密鍵に改行がある為)

class LoggerCritical(Exception):     #オリジナルの例外
    def __init__(self, message="重大Error"):
        self.message = message
        super().__init__(self.message)


@app.exception_handler(HTTPException)   #内部＋外部(詳細)Error, クライアントに詳細を返す際に使用
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"http_exc===={exc.detail}===={exc.status_code}")
    return JSONResponse(     #既にstatus_code = 400とdetailを返しているため不要
        content = exc.detail
    )

@app.exception_handler(LoggerCritical)    #内部＋外部(簡易)Error
async def critical_exception_handler(request: Request, exc: LoggerCritical): #excには例外の『インスタンス＝Obj』が自動で渡される(外見はメッセージ文だが、型はObj)
    logger.critical(f"critical_exc===={str(exc.__cause__)}===={str(exc)}") #exc.__cause__はfrom eのe。エラーメッセをcatch, str無くても表せるが、excはあくまでもobjなので、strを使った方が適切。
    return JSONResponse(
        status_code = 500,  #contentで無いため表示されない
        content = {"error": True, "message": "伺服器內部錯誤 Internal Server Error"}
    )

@app.exception_handler(Exception)   #全てのEndポイントで発生する未処理の例外をキャッチ(raise無しのerr, try囲んでなくてもキャッチ)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"global_exc===={str(exc.__cause__)}===={str(exc)}")
    return JSONResponse(
        status_code = 500,
        content = {"error": True, "message": "伺服器內部錯誤 Internal Server Error"}
    )


#  Connection Poolの設定　dbconfigは、データベース接続の設定を含む辞書
dbconfig = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}

try:
    connection_pool = pooling.MySQLConnectionPool(
        pool_name="mypool",
        pool_size=10,  # プールの最小接続数
        pool_reset_session=True, #接続がプールに返却されるたびにセッションがリセットされ、次の利用時にクリーンな状態で使用可能に
        **dbconfig
    )
    logger.debug("成功connection_pool")
except Error as e:
    raise LoggerCritical(f"失敗connection_pool{e}")


def connect_db():  #データベース接続オブジェクトはwith文が使える
    connection = connection_pool.get_connection()
    return connection





# def connect_db():  #データベース接続オブジェクトはwith文が使える
#     conn = mysql.connector.connect(
#             host = os.getenv("DB_HOST"),
#             user = os.getenv("DB_USER"),
#             password = os.getenv("DB_PASSWORD"),
#             database = os.getenv("DB_NAME")
#         )
#     if conn.is_connected():
#         logger.debug("成功connect_db")
#         return conn
#     raise LoggerCritical("失敗connect_db")
