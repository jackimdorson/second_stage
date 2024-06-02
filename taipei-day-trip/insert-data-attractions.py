# JSONデータの読み込みとMySQLへの保存
from common import connect_db
import json    #day-trip.jsonからのデータ取得必要
import re
from contextlib import contextmanager    #contextmanager=リソースの取得と解放を自動的に行うための仕組み(file操作,db接続,network)__enter__と__exit__という2つのメソッドを持つオブジェクト


@contextmanager                          #関数をコンテキストマネージャとして機能させるために使用
def get_cursor(db_conn):
    with db_conn.cursor() as cursor:     #リソースの取得__enter__メソッドとして機能
        try:
            yield cursor       #リソースをwith文のasに渡す：yieldは関数の実行を一時停止し、値を呼び出し元に返すが、関数の状態を保持。次に関数が再開されると、yieldの直後から実行が再開。ジェネレータ関数とは、yieldキーワードを使って値を一時的に返し、関数の実行を一時停止する関数
        except Exception as e:     #__exit__メソッドとして機能
            db_conn.rollback()
            raise Exception(f"yield停止中, 內部出問題") from e
        else:         #tryブロック内のコードは、例外を発生させなかった場合にのみ実行される。tryブロック内に多くのコードを含めると、意図しない例外が捕捉される可能性がある。
            db_conn.commit()



def enable_proper_auto_increment(cursor, table, column, value):   #dbのauto_incrementはinsert ignore等insertと言う行為があればカウントされる為、insertの分岐が必要
    try:
        cursor.execute(f"SELECT id FROM {table} WHERE {column} = %s", (value,))
    except Exception as e:
        raise Exception("SQL出問題:發生地=def enable_proper-1") from e
    row_id = cursor.fetchone()
    if row_id is None:
        try:
            cursor.execute(f"INSERT INTO {table} ({column}) VALUES (%s)", (value,))
        except Exception as e:
            raise Exception("SQL出問題:發生地=def enable_proper-2") from e
        return cursor.lastrowid   #直前のINSERTまたはUPDATEステートメントによって生成されたAUTO_INCREMENT列の値を取得。直前がselectでは使えない。
    return row_id[0]



def insert_data(db_conn, json_dict):
    with get_cursor(db_conn) as cursor:
        for results in json_dict["result"]["results"]:
            mrt = results["MRT"] if results["MRT"] is not None else 'Unknown'    #one of mrt　has null

            # Insert Mrts and Categories Tables
            mrt_id = enable_proper_auto_increment(cursor, "mrts", "name", mrt)
            category_id = enable_proper_auto_increment(cursor, "categories", "name", results["CAT"])

            # Insert Attraction Table
            try:
                cursor.execute("""
                    INSERT INTO attractions (name, description, address, transport, latitude, longitude, rate, mrt_id, category_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,(
                    results["name"], results["description"], results["address"], results["direction"],
                    results["latitude"], results["longitude"], results["rate"], mrt_id, category_id
                ))
            except Exception as e:
                raise Exception("SQL出問題:發生地=def insert_data-1") from e

            # For Inserting Images Table, Getting attraction ID
            attraction_id = cursor.lastrowid

            # Insert Image Table
            urls = re.findall(r"https://.*?\.(?:jpg|png)", results["file"], re.IGNORECASE)   #r""は\を認識 re.IGNORECASEは、大文字と小文字を区別しない
            try:
                for url in urls:
                    cursor.execute("INSERT INTO images (url, attraction_id) VALUES (%s, %s)", (url, attraction_id))
            except Exception as e:
                raise Exception("SQL出問題:發生地=def insert_data-2") from e



def data_exists(db_conn):
    with db_conn.cursor() as cursor:
        try:
            cursor.execute("SELECT COUNT(*) FROM mrts")
        except Exception as e:
            raise Exception("SQL出問題:發生地=def data_exists-1") from e
        count = cursor.fetchone()[0]
        if (count > 0):
            return True
        return False



def main():
    with connect_db() as db_conn:   #在common.py有處理try, catch
        if data_exists(db_conn):
            raise Exception("db已有資料,無法再加:發生地=def main-1")
        try:
            with open("data/taipei-attractions.json", "r", encoding="utf-8") as json_fileobj:
                json_dict = json.load(json_fileobj)   #fileObj(json)を読み取り → dict
                insert_data(db_conn, json_dict)      #上の関数の呼び出し
        except FileNotFoundError as e:      #指定したファイルが存在しない(名前miss, pathミス) **エラーによって異なる処理が必要な時はエラーを分ける。<->エラーの種類が少ない場合は分けない。
            raise Exception("with open(.json)出問題:FileNotFound:發生地=def main-2") from e
        except json.JSONDecodeError as e:   #JSONfileは存在するが不正な形式
            raise Exception("with open(.json)出問題:InvalidJsonFile:發生地=def main-3") from e
        except Exception as e:
            raise Exception("with open(.json)出問題:發生地=def main-4") from e


if __name__ == "__main__":   #ターミナルから直接python3 data_loader.py実行された場合のみmain()を実行するの意味
    main()