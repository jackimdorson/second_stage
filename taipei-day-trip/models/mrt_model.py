import config.db_config as mydbconfig


class MrtModel:
    def get_mrt_list():
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