import requests
from dotenv import load_dotenv
import os
import lstdb2
from datetime import datetime, timedelta


class ZparmFetcher:
    load_dotenv()
    # user = os.getenv("USER")
    # password=os.getenv("PASSWORD")
    # user=os.getenv("USER")
    _token=None
    _expires_at=None
    
    def __init__(self):
        '''
        init the variable to be used in functions.
        '''
        self.user = os.getenv("USER")
        self.password = os.getenv("PASSWORD")
        self.hostname=os.getenv("hostname")
        self.port=os.getenv("port")
        self.ipaddr=os.getenv("ipaddr")
        self.serviceName = os.getenv("serviceName")
        # print(serviceName)
        self.product = os.getenv("product")
        self.views = os.getenv("views_zparmsp")
        self.context = os.getenv("context")
        self.craport = os.getenv("craport")
        self.host_name = self.hostname
        self.port_num = self.craport
        self.url_link = "http://"+self.host_name+":"+self.port_num+"/cra/"
        self.get_data_view_api = "serviceGateway/services"+\
                "/products/"+self.product+"/views/"+self.views+"/data"
        self.url_endpoint = self.url_link + self.get_data_view_api
        # seserviceName =  serviceName 
    
    def _login(self) -> any :
        '''
        private function to call login internally
        '''
        login_service_api = "serviceGateway/services/"+self.serviceName+"/login"
        login_url = self.url_link + login_service_api
        # print(login_url)
        data = { "username":f"{self.user}","password":f"{self.password}"}
        # params = {"serviceName" : service_name }
        headers = {"Accept":"application/json",
                "Content-Type": "application/json; charset=utf-8"}
        r = requests.post(login_url,
                        json=data,
                        headers=headers
                        )
            
        if r.status_code == 200:
            # print(r.json())
            return [r.json(),r.headers]
        else:
            return r.status_code


    def get_data_view(self,get_data_url : str , token : str , context: str,startRow :int ,rows: int,) -> any:
    
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
            
        if r.status_code ==200:
                    
            return r.json()
        else:
            r.status_code

    def getzparm_value(self,checkzparm : str ,context : str ):
    
    
  
        # url_link="http://"+host_name+":"+port_num+"/cra/"
        # product = product
        # views = views
        # print(build_url(url_link,product,views))
        # url_endpoint = build_url(url_link,product,views)
        # db2_monitored=["DMU1DB2A","DNK3","DECD","DLK1"]
        db2_monitored = lstdb2.list_monitored_Db2("CURRSYS")
        context = self.get_target(db2_monitored,context)
        if context == "NotFound":
            return f"Only following Db2 targets {db2_monitored} are monitored. Select one of this."
        
        # context = context
        res_userToken =  self._getlogin()
        print(res_userToken) 
            
        text = self.get_data_view(self.url_endpoint,res_userToken["userToken"],context,startRow=1,rows=99999)

        if "error" in text.keys():
            # print(text['error'])
            return (f"api error:  {(text['error'])}")

        for x in text['Rows']:
            if x['Y400PRMN'] == checkzparm :
                return(self._mappingfunction(x))
    
    def _mappingfunction(self,some_dict :dict):
        mapping={
            "Y400PRMN": "zparm_name" ,
            "Y400ZVAL" : "zparm_value",
            "Y400PANL" : "panel name on Db2 install clist" ,
            "Y400INFO" : "online update allowed" ,
            "Y400MACN" : "db2 macro name",
            "Y4DB2ID": "db2 ssid",
        }
        mapped_response ={}
        for key in mapping.keys() :
            mapped_response[mapping[key]] = some_dict[key]
        return mapped_response

    def get_target(self,listdb2 : list , chkdb2 : str) -> str:
        db2found = False
        for x in listdb2:
            if (chkdb2.lower() == x['db2_ssid'].lower() or chkdb2.lower() == x['target_context'].lower()):
                db2found=True
                return x['target_context']
        if db2found == False :
            return "NotFound"
    
    def _getlogin(self):
        if ZparmFetcher._token == None :
            _login_info = self._login()
            ZparmFetcher._token = _login_info[0]
            expiry = int(_login_info[1]['Keep-Alive'].split('=')[1])
            ZparmFetcher._expires_at = timedelta(minutes=expiry) + datetime.now()
        else :
            if datetime.now() >= ZparmFetcher._expires_at:
                _login_info = self._login()
                ZparmFetcher._token = _login_info[0]
                expiry = int(_login_info[1]['Keep-Alive'].split('=')[1])
                ZparmFetcher._expires_at = timedelta(minutes=expiry) + datetime.now()

        return ZparmFetcher._token


if __name__ == "__main__":
   z = ZparmFetcher()
#    print(int(z.getlogin()[1]['Keep-Alive'].split('=')[1]))
#    print(z._getlogin())
   checkzparm="SYSADM2"
   context="DNK3"
   print(z.getzparm_value(checkzparm,context))
   print(z.getzparm_value(checkzparm,"DMU1DB2A"))