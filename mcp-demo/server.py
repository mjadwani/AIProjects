from mcp.server.fastmcp import FastMCP
import sys
sys.path.append("C:\\Users\\mjadwani\\Documents\\langgraphpractice")

import zparmsp
import lstdb2
import impact
import ragstep

mcp = FastMCP("zParmFetcherServer",host="0.0.0.0",port=8000)

# @mcp.tool()
# def get_cpu_usage() -> str:
#     '''
#     returns current cpu of Db2
#     '''
#     return "Current CPU Usage = 72%"

# @mcp.tool()
# def get_db2_status() -> str:
#     '''
#     returns health of Db2
#     '''
#     return "DB2 subsystem PROD1 is healthy"

# @mcp.resource("system://version")
# def get_version():
#     return "Monitoring Server v1.0"

# @mcp.tool()
# def hello(name: str) -> str:
#     '''
#     say hello to the caller
#     '''
#     return(f"hello {name}")

@mcp.tool()
def getzparmvaluetool(zparm : str , context :str ):
    ''' this tool returns the value of a zparm .
    function takes zparm as input 
    zparm is parameter name db2 configuration value 
    context is the target db2 name monitored by the backend api 
    zparms are also called subsystem parameters 
    Args:
        zparm: The parameter name (e.g., 'TCPALVER').
        context: The Db2 name or the Db2 Target Name.
    
    This tool should be used when:
        - user asks for a zparm value
        - user asks whether a zparm differs between subsystems
        - user asks to compare a specific zparm across multiple Db2 systems

    For specific zparm or list of zparms comparisons:
        1. Call this tool once per subsystem.
        2. Compare returned values.
    '''
    
    return zparmsp.getzparm_value(zparm,context)

@mcp.tool()
def getzparm_alltool(context :str ):
    ''' this tool returns dictionary of all zparm values for the context .
    return value contains zparmname and tuple containing its value and macroname where zparm lives.
    function takes context as input 
    context is the target db2 name monitored by the backend api 
    zparms are also called subsystem parameters '''
    return zparmsp.getzparm_all(context)

@mcp.tool()
def comparezparm_tool(ssid1 :str , ssid2 :str ):
    ''' 
    
    Purpose:
    Compare ALL zparm settings between two Db2 subsystems.

    Use ONLY when the user requests:
    - all zparms
    - complete zparm comparison
    - differences between two subsystems
    - compare every zparm

    DO NOT USE when:
    - user asks for a specific zparm
    - user asks for one or more named zparms such as CMTSTAT, EDMPOOL, TCPALVER
    - user asks for the value of a single zparm

    For specific zparm comparisons, call getzparmvaluetool for each subsystem and compare the results.
    
    This tool compare ALL zparms of db2 ssid1 with ssid2
    returns dictionary of 2 keys 
    1 : non matching zparms and their settings
    2 : non existing zparms , existing in ssid1 but not in ssid 2
    
    function takes 2 parameter as input which are db2 ssid.
    zparms are also called subsystem parameters 
    
    '''
    return zparmsp.zparm_compare([ssid1,ssid2])

@mcp.tool()
def list_monitored_Db2tool(context :str ):
    ''' Function :Purpose to show all the Db2 that are being monitored 
        Accepts context as input which is CURRSYS .
        Returns a dictionary where key is target db2 monitored and value is db2 subsystem id.
    '''
    return lstdb2.list_monitored_Db2(context)

@mcp.tool()
def get_relationships_tool(node : str):
    '''
    Purpose :
    Takes zparm as input find its relation with the effect it can cause.
    '''
    return impact.get_direct_impacts(node)

@mcp.tool()
def get_impact_chain_tool(node : str):
    '''
    Purpose :
    Takes zparm as input and reasons out complete Impact it can cause.
    '''
    return impact.get_impact_chain(node)

@mcp.tool()
def find_relationship_tool(node1 : str , node2 : str ):
    '''
    Purpose :
    Takes two input and tries to find the relationship between them.
    '''
    return impact.find_path(node1,node2)

@mcp.tool()
def db2_rag_tool(query: str):
    '''
    use this tool to refer pdf documentation related to Db2 zparms.
    document it refers is for Db2 v13. Use it to explain user questions related to
    zparm explainations and value limits and impacts. While replying put your perpective from datasharing db2 also
    When user specifies text instead of actual zparm name check in documentation for actual value of zparm . 
    For eg. tcp already verified is text is TCPALVER is actual zparm name.

    '''
    resultrag = ragstep.get_retriever().invoke(query)
    content =[doc.page_content for doc in resultrag]
    metadata =[doc.metadata for doc in resultrag]
    return {
        'query' : query,
        'content' : content,
        'metadata' : metadata
    }

if __name__ == "__main__":
    mcp.run( transport="streamable-http")