import requests
from dotenv import load_dotenv
load_dotenv()
import os
password=os.getenv("PASSWORD")
user=os.getenv("USER")
print(f"User : {user} Password :{password}")

headers = {"Accept":"application/json",
               "Content-Type": "application/json; charset=utf-8",
               "Authorization": f"Basic {user}:{password}" }

# h =  f""" "Accept":"application/json", 
#         "Content-Type": "application/json; charset=utf-8", 
#         "Authorization": "Basic {user}:{password}" 

# """

# headers1 ={ h }

# print(type(headers) , type(headers1))

print(headers)