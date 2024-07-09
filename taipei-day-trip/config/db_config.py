#Standard Lib
import os  #getenv()...環境変数(.env)の読み込みに必要

#3rd-party Lib
import mysql.connector #pooling(Connection Poolの設定), Error

#Local Lib
import handlers.exception_handlers as myexception


private_key = os.getenv("PRIVATE_KEY").replace("\\n", "\n")   #秘密鍵を取得し、改行を適切に処理(秘密鍵に改行がある為)


dbconfig = {  #Connection Poolの設定　dbconfigは、データベース接続の設定を含む辞書
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}

try:
    connection_pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="mypool",
        pool_size=10,  # プールの最小接続数
        pool_reset_session=True, #接続がプールに返却されるたびにセッションがリセットされ、次の利用時にクリーンな状態で使用可能に
        **dbconfig
    )
    myexception.logger.debug("成功connection_pool")
except mysql.connector.Error as e:
    raise myexception.LoggerCritical("失敗connection_pool") from e


def connect_db():  #データベース接続オブジェクトはwith文が使える
    connection = connection_pool.get_connection()
    return connection