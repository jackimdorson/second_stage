#Local Lib
import config.db_config as mydbconfig


class AttractionModel:
    @staticmethod
    def get_all(size: int, page: int, keyword: str | None) -> list[dict | None]:
        with mydbconfig.connect_db() as db_conn:
            with db_conn.cursor(dictionary=True) as cursor:  #預設tuple -> dictで返ってくる, cursorObjの生成が失敗することはない。
                try:
                    if not keyword:
                        cursor.execute("""
                            SELECT a.id, a.name, categories.name AS category, a.description, a.address, a.transport, mrts.name AS mrt, a.latitude AS lat, a.longitude AS lng
                            FROM attractions AS a
                            INNER JOIN mrts ON a.mrt_id = mrts.id
                            INNER JOIN categories ON a.category_id = categories.id
                            ORDER BY a.id
                            LIMIT %s OFFSET %s
                        """,(size, page * size))    #LIKE"%keyword%"の形 keywordは二箇所に格納される
                    else:
                        cursor.execute("""
                            SELECT a.id, a.name, categories.name AS category, a.description, a.address, a.transport, mrts.name AS mrt, a.latitude AS lat, a.longitude AS lng
                            FROM attractions AS a
                            INNER JOIN mrts ON a.mrt_id = mrts.id
                            INNER JOIN categories ON a.category_id = categories.id
                            WHERE mrts.name = %s OR a.name LIKE %s
                            ORDER BY a.id
                            LIMIT %s OFFSET %s
                        """,(keyword, f"%{keyword}%", size, page * size))
                    attractions = cursor.fetchall()     #返り値は　[ { },{ } ]  or  None
                    if not attractions:
                        return []   #return後需要len, 因此不得使用False, None
                    for attraction in attractions:
                        cursor.execute(
                            "SELECT url FROM images WHERE attraction_id = %s",(attraction["id"],))
                        attraction["images"] = [row["url"] for row in cursor.fetchall()]
                except Exception as e:
                    raise Exception("SQL出問題:發生地=def get_all-1") from e
                return attractions


    @staticmethod
    def get_detail(attraction_id: int) -> dict:
        with mydbconfig.connect_db() as db_conn:
            with db_conn.cursor(dictionary=True) as cursor:
                if attraction_id > 58:
                    return False
                try:
                    cursor.execute("""
                        SELECT a.id, a.name, categories.name AS category, a.description, a.address, a.transport, mrts.name AS mrt, a.latitude AS lat, a.longitude AS lng
                        FROM attractions AS a
                        INNER JOIN mrts ON a.mrt_id = mrts.id
                        INNER JOIN categories ON a.category_id = categories.id
                        WHERE a.id = %s
                        ORDER BY a.id
                    """,(attraction_id,))            #%sの代入は例え、dictionary=Trueだとしても、tupleであることに注意。
                    attraction = cursor.fetchone()     #返り値は　{ }  or  None
                    if attraction is None:    #fetchoneはなければNoneを返す、この記述は少しだけ高速。fetchallはListを返す為, if not attra...の記述法
                        return False
                    cursor.execute("SELECT url FROM images WHERE attraction_id = %s", (attraction["id"],))
                    attraction["images"] = [row["url"] for row in cursor.fetchall()]
                except Exception as e:
                    raise Exception("SQL出問題:發生地=def get_detail-1") from e
                return attraction


class MrtModel:
    @staticmethod
    def get_mrt_list() -> list[str]:
        with mydbconfig.connect_db() as db_conn:
            with db_conn.cursor(dictionary=True) as cursor:
                try:
                    cursor.execute("""
                        SELECT mrts.name, COUNT(a.id) AS a_count
                        FROM mrts
                        INNER JOIN attractions As a ON mrts.id = a.mrt_id
                        WHERE mrts.name != 'Unknown'
                        GROUP BY mrts.name
                        ORDER BY a_count DESC
                    """)
                    mrt_list = [row["name"] for row in cursor.fetchall()]
                    return mrt_list
                except Exception as e:
                    raise Exception("SQL出問題:發生地=def get_mrt_list-1") from e