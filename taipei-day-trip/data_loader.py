# JSONデータの読み込みとMySQLへの保存
import json
from common import connect_db, setup_logger

logger = setup_logger()


def insert_data(connect_db, data):
    try:
        with connect_db.cursor() as cursor:
            try:
                for json in data["result"]["results"]:
                    # Insert MRT and Category
                    cursor.execute("INSERT INTO mrts (name) VALUES (%s)", (attraction["MRT"],))
                    cursor.execute("INSERT INTO categories (name) VALUES (%s)", (attraction["CAT"],))

                    # Get MRT and Category IDs
                    cursor.execute("SELECT id FROM mrts WHERE name = %s", (attraction["MRT"],))
                    mrt_id = cursor.fetchone()[0]
                    cursor.execute("SELECT id FROM categories WHERE name = %s", (attraction["CAT"],))
                    category_id = cursor.fetchone()[0]

                    # Insert Attraction
                    cursor.execute("""
                        INSERT INTO attractions (name, description, address, transport, rate, latitude, longitude)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,(
                        attraction["name"], attraction["description"], attraction

                    ))






            except Exception as e:
                logger.error(f"==== SQL發生Error : {e} ====")
    except Exception as e:
        logger.error(f"==== mydb.cursor()發生Error : {e} ====")


def main():
    with connect_db() as connect_db:
        try:
            with open("taipei-attractions.json", "r", encoding="utf-8") as json_fileobj:
                json_dict = json.load(json_fileobj)   #fileObj(json)を読み取り → dict
            insert_data(connect_db, json_dict)
        except FileNotFoundError:  #指定したファイルが存在しない(名前miss, pathミス)
            logger.error("===== FileNotFoundError : Not Found =====")
        except json.JSONDecodeError:   #JSONfileは存在するが不正な形式
            logger.error("===== JSONDecodeError : Invalid JSON file =====")
        except Exception as e:
            logger.error(f"==== JSONFile發生Error : {e} ====")

