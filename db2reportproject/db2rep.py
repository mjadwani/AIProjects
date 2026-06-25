
from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth
import os
import pandas as pd
import http.client
http.client.HTTPConnection.debuglevel = 0

x= load_dotenv(verbose=True)
password=os.getenv("PASSWORD")
user=os.getenv("USER")
hostname=os.getenv("hostname")
port=os.getenv("port")
ipaddr=os.getenv("ipaddr")
port = os.getenv("port_dmu1")

# POST https://<host>:<port>/services/<serviceCollectionID>/<serviceName>/<version>
def func_max_min_date(serviceCollectId :str = "MJREST" , 
                      serviceName :str ="PRACMXMIDT", 
                      version :str ="V1" ):
    
    maxdate_api = f"http://{hostname}:{port}/services/{serviceCollectId}/{serviceName}/{version}"
    
    # print(maxdate_api)
    
    headers = {
                "Accept":"application/json",
               "Content-Type": "application/json; charset=utf-8"
                }
    r = requests.post(maxdate_api,
                    #   json=data,
                      headers=headers,
                      auth=HTTPBasicAuth(user, password)
                      )
        
    if r.status_code == 200:
        # print(r.json())
        max_date_time = r.json()['ResultSet Output'][0]["MAXDATETIME"]
        min_date_time = r.json()['ResultSet Output'][0]["MINDATETIME"]
        num_rows = r.json()['ResultSet Output'][0]["NUMROWS"]
        return{"max_date_in_table" : max_date_time , 
               "min_date_in_table" : min_date_time ,
               "num_of_rows_in_table": num_rows}
    else:
        return {"Error :" : r.status_code    }
    
def func_accounting_by_hour_authid(serviceCollectId :str = "MJREST" , 
                      serviceName :str ="PRACCHR4", 
                      version :str ="V1",
                       db2ssid : str="DMU1",
                        authid :str ="BMCADM",
                         inpdate : str ="05/28/2026" ):
    
    accnt_by_hr_endpoint = f"http://{hostname}:{port}/services/{serviceCollectId}/{serviceName}/{version}"
    
    # print(accnt_by_hr_endpoint)
 
    data = {
        "INPSSID" : db2ssid,
        "INPAUTHID"  : authid,
        "MYDAY" : inpdate
    }
    # print(data)
    headers = {
                "Accept":"application/json",
               "Content-Type": "application/json; charset=utf-8"
                }
    r = requests.post(accnt_by_hr_endpoint,
                      json=data,
                      headers=headers,
                      auth=HTTPBasicAuth(user, password)
                      )
        
    if r.status_code == 200:
        # print(r.json())
        md_data = convert_to_markdown_for_llm(r.json())  #mark_down data
        return md_data
       
    else:
        return {"Error :" : r.status_code    }
    
def convert_to_markdown_for_llm(api_response):
    raw_data = api_response.get('ResultSet Output', [])
    if not raw_data:
        return "No data found."
        
    df = pd.DataFrame(raw_data)
    
    return df.to_markdown(index=False)

def func_accounting_by_authid(serviceCollectId :str = "MJREST" , 
                      serviceName :str ="PRACTRID", 
                      version :str ="V1",
                       db2ssid : str="DMU1",
                        authid :str ="MVSMKJ",
                         inpdate : str ="05/29/2026",
                          hr1: str ="03",
                            ):
    
    accnt_by_authid_endpoint = f"http://{hostname}:{port}/services/{serviceCollectId}/{serviceName}/{version}"
    
    # print(accnt_by_authid_endpoint)
    
    # a = hr1 + 2
    
    # print(inphr2)
    data = {
        "INPSSID" : db2ssid,
        "INPAUTHID"  : authid,
        "MYDATE" : inpdate,
        "INPHR1" : hr1,
       
    }
    # print(data)
    headers = {
                "Accept":"application/json",
               "Content-Type": "application/json; charset=utf-8"
                }
    r = requests.post(accnt_by_authid_endpoint,
                      json=data,
                      headers=headers,
                      auth=HTTPBasicAuth(user, password)
                      )
        
    if r.status_code == 200:
        # print(r.json())
        md_data = convert_to_markdown_for_llm(r.json())  #mark_down data
        return md_data
       
    else:
        return {"Error :" : r.status_code    }
    

def func_accounting_by_anyid(serviceCollectId :str = "MJREST" , 
                            serviceName :str ="PRACNID", 
                            version :str ="V1",
                            db2ssid : str="DMU1",
                            inpdate : str ="05/29/2026",
                            hr1: str ="03"
                            ):
    
    accnt_by_anyid_endpoint = f"http://{hostname}:{port}/services/{serviceCollectId}/{serviceName}/{version}"
    
    # print(accnt_by_anyid_endpoint)
    # print(accnt_by_authid_endpoint)
    
    # a = hr1 + 2
    
    # print(inphr2)
    data = {
        "INPSSID" : db2ssid,
        "MYDATE" : inpdate,
        "INPHR" : hr1,
       
    }
    # print(data)
    headers = {
                "Accept":"application/json",
               "Content-Type": "application/json; charset=utf-8"
                }
    r = requests.post(accnt_by_anyid_endpoint,
                      json=data,
                      headers=headers,
                      auth=HTTPBasicAuth(user, password)
                      )
        
    if r.status_code == 200:
        # print(r.json())
        md_data = convert_to_markdown_for_llm(r.json())  #mark_down data
        return md_data
       
    else:
        return {"Error :" : r.status_code    }
if __name__ == "__main__":
    
    collection_id = "MJREST"
    service_name ="PRACCHR4"
    version = "V1"
    # print(func_max_min_date(collection_id,service_name,version))
    # print(func_max_min_date())
    print(func_accounting_by_hour_authid())
    # print(func_accounting_by_authid(hr1="03"))
    
    # dt = ['05/27/2026','05/28/2026','05/29/2026','05/30/2026','05/31/2026']

    # for x in dt:
    #     print(func_accounting_by_anyid(inpdate=x,hr1="14"))
