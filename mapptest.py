some_dict ={"DECD": "DECD", "DLK1": "DLK1", "DMU1DB2A": "DMU1", "DNK3": "DNK3"}

def mappingfunction(some_dict :dict):
    mapping=["target_context", "db2_ssid"] 
    mapped_response =[]
    for key in some_dict.keys():
        mapped_response_dict ={}
        mapped_response_dict[mapping[0]] = key
        mapped_response_dict[mapping[1]] = some_dict[key]
        mapped_response.append(mapped_response_dict)
    return mapped_response

mappingfunction(some_dict)
print(mappingfunction(some_dict))