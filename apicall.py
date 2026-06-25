import requests
from dotenv import load_dotenv
load_dotenv()
import os
password=os.getenv("PASSWORD")
user=os.getenv("USER")
hostname=os.getenv("hostname")
port=os.getenv("port")
ipaddr=os.getenv("ipaddr")
# print(f"""User : {user} Password :{password}" 
#     "hostname" : {hostname} 
#     "port" : {port}      
#       """)

def get_data(url_link : str , service_name: str  ) -> any :
    login_url = url_link + service_name
    
    headers = {"Accept":"application/json",
               "Content-Type": "application/json; charset=utf-8",
               "Authorization": f"Basic {user}:{password}" }
    
    
    r = requests.post(login_url,
                        # json=data,
                      headers=headers,
                      stream=True
                      )
        
    if r.status_code == 200:
        # print("Response:", r.json())
        return r.json()
    else:
        # print(r.status_code)
        return (r.status_code)
        
    
def authid() :
    # print("Starting the application...")
    # host_name = "172.24.48.166" 
    host_name = hostname
    # port_num = "7705"   #dmu1
    port_num = port
    end_point = "/services"
    serviceName = "/MJREST/TESTOTEL"
    # numberofdays = 5

    url_link="http://"+host_name+":"+port_num+end_point

             
    response =  get_data(url_link,serviceName)
    # print(response)
    # print("Application finished.")
    return response['ResultSet Output'][0]['C4']

def main() :
    # print("Starting the application...")
    # host_name = "172.24.48.166" 
    host_name = hostname
    # port_num = "7705"   #dmu1
    port_num = port
    end_point = "/services"
    serviceName = "/MJREST/TESTOTEL"
    # numberofdays = 5

    url_link="http://"+host_name+":"+port_num+end_point

             
    response =  get_data(url_link,serviceName)
    # print(response)
    # print("Application finished.")
    return response

def authid() :
    response = main()
    return response['ResultSet Output'][0]['C4']

def workstation() :
    response = main()
    return response['ResultSet Output'][0]['C5']

def fullresponse() :
    response = main()
    return response['ResultSet Output'][0]
        
if __name__ == "__main__":
    main()

    