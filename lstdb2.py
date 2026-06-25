import requests
from dotenv import load_dotenv
import json
import os

load_dotenv()

password=os.getenv("PASSWORD")
user=os.getenv("USER")
hostname=os.getenv("hostname")
port=os.getenv("port")
ipaddr=os.getenv("ipaddr")
serviceName = os.getenv("serviceName")
# print(serviceName)
product = os.getenv("product")
views = os.getenv("views_stdb2")
context = os.getenv("context")
craport = os.getenv("craport")
host_name = hostname
port_num = craport
serviceName =  serviceName 

def login(url_link : str , service_name: str ) -> any :
    login_service_api = "serviceGateway/services/"+service_name+"/login"
    login_url = url_link + login_service_api
    # print(login_url)
    data = { "username":f"{user}","password":f"{password}"}
    # params = {"serviceName" : service_name }
    headers = {"Accept":"application/json",
               "Content-Type": "application/json; charset=utf-8"}
    r = requests.post(login_url,
                      json=data,
                      headers=headers
                      )
        
    if r.status_code == 200:
        # print(r.json())
        return r.json()
    else:
        return r.status_code

def build_url(url_link : str , #service_name: str , 
                   productName : str ,views :str
                  
                  ) -> any:
    
    # url_endpoint =[]
    get_data_view_api = "serviceGateway/services"+\
                "/products/"+productName+"/views/"+views+"/data"
    url_endpoint = url_link + get_data_view_api
    
    return url_endpoint

def get_data_view(get_data_url : str , token : str , context: str,startRow :int ,rows: int,) -> any:
    
    params ={
        "context":context,
        "server": "*",
        "system" : "*",
        "scope" : "*",
        "period" : "=",
        "startRow": startRow,
        "rows":rows,
        "refresh":"Y",
        "close":"Y",
        "filter":"null",
        "sort":"null",
        "session":"null"

    }
    headers = {"Accept":"application/json",
               "Authorization":"Bearer "+token ,
               "Content-Type": "application/json; charset=utf-8"}
    
    # for get_data_url in url_endpoint:
    # print(get_data_url)
    r = requests.get(get_data_url,
                        params=params,
                        headers=headers,
                        stream= True
                        )
        # print(r.request.url)
        # print(r.status_code)
        # print(r.json())
    if r.status_code ==200:
        # with open("temp.json",'wb') as f:
        #     for each in r.iter_content(chunk_size=512):
        #         if each:
        #             f.write(each)
            
        # return "All good"

    
        return r.json()
    else:
        r.status_code

def list_monitored_Db2(context: str ="CURRSYS"):
    
    
  
    url_link="http://"+host_name+":"+port_num+"/cra/"
    # product = product
    # views = views
    # print(build_url(url_link,product,views))
    url_endpoint = build_url(url_link,product,views)
    # db2_monitored=["DMU1DB2A","DNK3","DECD","DLK1","CURRSYS"]
    # if context not in db2_monitored:
    #     return f"Only following Db2 targets {db2_monitored} are monitored. Select one of this."
    
    context = context
    res_userToken =  login(url_link,serviceName)
    # print(res_userToken) 
        
    text = get_data_view(url_endpoint,res_userToken["userToken"],context,startRow=1,rows=99999)

    if "error" in text.keys():
        # print(text['error'])
        return (f"api error:  {(text['error'])}")

    list_of_db2_monitored_with_context={}

    # print(text["Rows"])
    for x in text['Rows']:
        key=x['STDB2TARG']
        list_of_db2_monitored_with_context[key] = x['STDB2ID']
    return(mappingfunction(list_of_db2_monitored_with_context))
        
def mappingfunction(some_dict :dict):
    mapping=["target_context", "db2_ssid"] 
    mapped_response =[]
    for key in some_dict.keys():
        mapped_response_dict ={}
        mapped_response_dict[mapping[0]] = key
        mapped_response_dict[mapping[1]] = some_dict[key]
        mapped_response.append(mapped_response_dict)
    return mapped_response

if __name__ == "__main__":
    checkzparm="ABIND"
    context="CURRSYS"
    print(list_monitored_Db2(context))
    # print(getzparmvalue(checkzparm,context))
    # print(getzparm_all(context))


#     zparmvalue(checkzparm)
    
    # host_name = hostname
    # port_num = craport
    # serviceName =  serviceName
  
    # url_link="http://"+host_name+":"+port_num+"/cra/"
    # product = product
    # views = views
    # print(build_url(url_link,product,views))
    # url_endpoint = build_url(url_link,product,views)
    # context = context
    # res_userToken =  login(url_link,serviceName)
    # print(res_userToken) 
        
    # text = get_data_view(url_endpoint,res_userToken["userToken"],context,startRow=1,rows=99999)

    # print(text['Rows'][0])

    # for x in text['Rows']:
    #     if x['Y400PRMN'] == 'ABIND':
    #         print(x)

