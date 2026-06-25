from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth
import os
import pandas as pd
import http.client
http.client.HTTPConnection.debuglevel = 0


'''
This function is to generate db2 report for any AUTHID .
All it needs a Date Interval --> START DATE and END DATE

'''

x= load_dotenv(verbose=True)
password=os.getenv("PASSWORD")
user=os.getenv("USER")
hostname=os.getenv("hostname")
port=os.getenv("port")
ipaddr=os.getenv("ipaddr")
port = os.getenv("port_dmu1")

def convert_to_markdown_for_llm(api_response):
    raw_data = api_response.get('ResultSet Output', [])
    if not raw_data:
        return "No data found."
        
    df = pd.DataFrame(raw_data)
    
    return df.to_markdown(index=False)

def func_anyid_getaccreport(serviceCollectId :str = "MJREST" , 
                            serviceName :str ="PRACNIDA", 
                            version :str ="V1",
                            db2ssid : str="DMU1",
                            begdate : str ="05/29/2026",
                            enddate : str ="05/30/2026",
                            
                            ):
    
    accnt_by_anyid_endpoint = f"http://{hostname}:{port}/services/{serviceCollectId}/{serviceName}/{version}"
    
    # print(accnt_by_anyid_endpoint)
    # print(accnt_by_authid_endpoint)
    
    # a = hr1 + 2
    
    # print(inphr2)
    data = {
        "INPSSID" : db2ssid,
        "BEGDATE" : begdate,
        "ENDDATE" : enddate,
       
       
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
    # print(func_accounting_by_hour_authid())
    # print(func_accounting_by_authid(hr1="03"))
    print(func_anyid_getaccreport())