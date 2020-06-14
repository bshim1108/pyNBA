from pyNBA.Data.sql import SQL
from pyNBA.Data.data import QueryData

if __name__ == "__main__":
    sql = SQL()
    sql.create_connection()
    sql.create_tables()

    query_data = QueryData()
    data = query_data.query_contest_info_data()
    print(data)