import os
os.add_dll_directory('C:\\Program Files\\IBM\\SQLLIB\\bin')
import ibm_db
from dotenv import load_dotenv

load_dotenv()
password=os.getenv("PASSWORD")
user=os.getenv("USER")
hostname=os.getenv("hostname")
port=os.getenv("port")
ipaddr=os.getenv("ipaddr")
port = os.getenv("port_dmu1")

# C:\Program Files\IBM\SQLLIB\clidriver\bin
# Connection string format

def func_sql_call(select_list_elem : list ) -> list :
    dsn = f"DATABASE=DMU;HOSTNAME={hostname};PORT={port};PROTOCOL=TCPIP;UID={user};PWD={password};"

    # try:
    #     conn = ibm_db.connect(dsn, "", "")
    #     print("Connection successful!")
    #     ibm_db.close(conn)
    # except Exception as e:
    #     print(f"Connection failed: {e}")

    conn = ibm_db.connect(dsn, "", "")

    select_list = ""
    for elem in select_list_elem :
        select_list = select_list + ","  + elem 

    select_list =  select_list.lstrip(",")
    print(select_list)
    # select_list = select_list_elem.split()
    table_schema= "MVSMKJ"
    table_name ="DMRACDTL"
    sql_statement = f"SELECT {select_list} from {table_schema}.{table_name} fetch first 5 rows only ; "
    sql_result =[]
    if conn:
        stmt = ibm_db.exec_immediate(conn,sql_statement)
        if stmt:
            while (ibm_db.fetch_row(stmt)):
                fetch_result = ibm_db.result(stmt, 0)
                sql_result.append(fetch_result)
        else:
            print(ibm_db.stmt_errormsg())
        ibm_db.commit(conn)
        ibm_db.close(conn)
        return sql_result
    else:
        print("No connection:", ibm_db.conn_errormsg())
        return ["No connection:", ibm_db.conn_errormsg()]
    
    print(sql_result)
    print('ODBC Test end')

if __name__ == "__main__":
    select_list_elem= ['AUTHID' ,'DATETIME' ]
    print(func_sql_call(select_list_elem ))
