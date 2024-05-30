from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os                          #環境変数(.env)の読み込みに必要
from dotenv import load_dotenv     #環境変数(.env)の読み込みに必要import json
import mysql.connector
import logging


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



class LoggerCritical(Exception):     #オリジナルの例外
    def __init__(self, message="重大Error"):
        self.message = message
        super().__init__(self.message)


@app.exception_handler(HTTPException)   #内部＋外部(詳細)Error, クライアントに詳細を返す際に使用
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"http_exc:{exc.detail}:{exc.status_code}")
    return JSONResponse(
        content = exc.detail
    )

@app.exception_handler(LoggerCritical)    #内部＋外部(簡易)Error
async def critical_exception_handler(request: Request, exc: LoggerCritical):
    logger.critical(f"critical_exc:{exc}")
    return JSONResponse(
        status_code = 500,
        content = {"message": "Internal Server Error"} #セキュリティから固定メッセ
    )

@app.exception_handler(Exception)   #raise("str")で明示的にエラーを出されたもののみcatch内部＋外部(簡易)Error
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"global_exc:{exc}")
    return JSONResponse(
        status_code = 500,
        content = {"message": "Internal Server Error"}  #セキュリティから固定メッセ
    )



def connect_db():  #データベース接続オブジェクトはwith文が使える
    conn = mysql.connector.connect(
            host = os.getenv("DB_HOST"),
            user = os.getenv("DB_USER"),
            password = os.getenv("DB_PASSWORD"),
            database = os.getenv("DB_NAME")
        )
    if conn.is_connected():
        logger.debug("成功connect_db")
        return conn
    raise LoggerCritical("失敗connect_db")