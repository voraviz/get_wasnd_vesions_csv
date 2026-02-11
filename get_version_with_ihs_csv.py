# full_inventory.py
import sys
import re

def clean_version(raw_string, is_java=False):
    """
    Extracts the numeric version string from raw output.
    """
    if not raw_string: return "Unknown"
    
    # Pattern for Java (1.8.0_351, 11.0.21, 8.0.5.30)
    if is_java:
        match = re.search(r'([0-9]+(\.[0-9]+)+(_[0-9]+|[\+][0-9]+)?)', raw_string)
    else:
        # Pattern for WAS/IHS (9.0.5.11, 8.5.5.20)
        match = re.search(r'([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)', raw_string)
    
    return match.group(1) if match else raw_string.split()[0]

def get_detailed_java(jvm_mbean):
    try:
        # Check multiple properties to find the patch level
        props = ['java.fullversion', 'java.runtime.version', 'java.version']
        combined = ""
        for p in props:
            combined += AdminControl.invoke(jvm_mbean, 'getProperty', p) + " "
        return clean_version(combined, True)
    except:
        return "N/A"

def get_inventory():
    print("Type,Hostname,Name,Java Version,Version")

    # --- 1. Process WebSphere Application Server Nodes ---
    nodes = AdminConfig.list('Node').splitlines()
    for node in nodes:
        node_name = AdminConfig.showAttribute(node, 'name')
        host_name = AdminConfig.showAttribute(node, 'hostName')

        # Try to find a running process (nodeagent or server)
        server_mbean = AdminControl.queryNames('type=Server,node=' + node_name + ',process=nodeagent,*')
        if not server_mbean:
            others = AdminControl.queryNames('type=Server,node=' + node_name + ',*').splitlines()
            if others: server_mbean = others[0]

        if server_mbean:
            was_ver = clean_version(AdminControl.getAttribute(server_mbean, 'serverVersion'))
            jvm_mbean = AdminControl.queryNames('type=JVM,node=' + node_name + ',process=' + AdminControl.getAttribute(server_mbean, 'name') + ',*')
            java_ver = get_detailed_java(jvm_mbean)
            print("WAS,%s,%s,%s,%s" % (host_name, node_name, java_ver, was_ver))
        else:
            print("WAS,%s,%s,Stopped,N/A" % (host_name, node_name))

    # --- 2. Process IBM HTTP Servers (IHS) ---
    webservers = AdminConfig.list('WebServer').splitlines()
    for ws in webservers:
        ws_name = AdminConfig.showAttribute(ws, 'name')
        # Get the node this webserver belongs to
        ws_node = ws.split('/nodes/')[1].split('/')[0]
        ws_host = AdminConfig.showAttribute(AdminConfig.getid('/Node:'+ws_node+'/'), 'hostName')
        
        # Try to get live version via MBean (Requires IHS Admin/NodeAgent to be active)
        ws_mbean = AdminControl.queryNames('type=WebServer,name=' + ws_name + ',*')
        if ws_mbean:
            try:
                # serverVersion for IHS usually returns "IBM_HTTP_Server/9.0.5.11 (Unix)"
                raw_ihs = AdminControl.getAttribute(ws_mbean, 'serverVersion')
                ihs_ver = clean_version(raw_ihs)
                print("IHS,%s,%s,N/A,%s" % (ws_host, ws_name, ihs_ver))
            except:
                print("IHS,%s,%s,N/A,Error" % (ws_host, ws_name))
        else:
            # If MBean isn't found, the webserver is likely unmanaged or stopped
            print("IHS,%s,%s,N/A,Stopped/Unmanaged" % (ws_host, ws_name))

if __name__ == "__main__":
    get_inventory()