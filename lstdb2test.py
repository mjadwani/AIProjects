# db2_monitored= [{'target_context': 'DECD', 'db2_ssid': 'DECD'}, {'target_context': 'DLK1', 'db2_ssid': 'DLK1'}, {'target_context': 'DMU1DB2A', 'db2_ssid': 'DMU1'}, {'target_context': 'DNK3', 'db2_ssid': 'DNK3'}]
import lstdb2



def get_target(listdb2 : list , chkdb2 : str) -> str:
    db2found = False
    for x in listdb2:
        if (chkdb2.lower() == x['db2_ssid'].lower() or chkdb2.lower() == x['target_context'].lower()):
            db2found=True
            return x['target_context']
    if db2found == False :
        return f"Only Following Db2's are being monitored for this API scope : \n {listdb2}"

if __name__=="__main__":
    db2_monitored = lstdb2.list_monitored_Db2("CURRSYS")
    print(get_target(db2_monitored,"DNK3"))
    print(get_target(db2_monitored,"DMU1DB2A"))
    print(get_target(db2_monitored,"DNKX"))