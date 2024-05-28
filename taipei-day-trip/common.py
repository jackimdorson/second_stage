import os                          #環境変数(.env)の読み込みに必要
from dotenv import load_dotenv     #環境変数(.env)の読み込みに必要import json
import mysql.connector
import logging


load_dotenv()   # 環境変数の読み込み

def connect_db():
    try:
        return mysql.connector.connect(
            host = os.getenv("DB_HOST"),
            user = os.getenv("DB_USER"),
            password = os.getenv("DB_PASSWORD"),
            database = os.getenv("DB_NAME")
        )
    except Exception as e:   #ExceptionはPythonの標準ライブラリに含まれる組み込みの例外クラス
        print(f"==== connect_db()發生Error : {e} ====")
        return None


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