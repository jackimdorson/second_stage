#config = システム全体の設定  dbconfig = 特にdbに特化した設定
import handlers.exception_handlers as myexception
import os      #getenv()...環境変数(.env)の読み込みに必要
import dotenv  #load_dotenv()...環境変数(.env)の読み込みに必要
import mysql.connector #pooling(Connection Poolの設定), Error


dotenv.load_dotenv()   # 環境変数の読み込み

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
    raise myexception.LoggerCritical(f"失敗connection_pool{e}")


def connect_db():  #データベース接続オブジェクトはwith文が使える
    connection = connection_pool.get_connection()
    return connection