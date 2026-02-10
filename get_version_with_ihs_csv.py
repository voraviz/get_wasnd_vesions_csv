# check_all_versions_csv.py
import sys

def get_all_versions():
    # Header for the CSV output
    print("Host Name,Node Name,Server Type,Server Name,Software Version,Java Version")

    # 1. Query all Server MBeans (includes App Servers, Dmgr, NodeAgents)
    all_servers = AdminControl.queryNames('type=Server,*').splitlines()
    
    # 2. Query all WebServer MBeans (IHS)
    web_servers = AdminControl.queryNames('type=WebServer,*').splitlines()

    # Combine both lists for processing
    total_list = all_servers + web_servers

    for mbean in total_list:
        try:
            # Extract basic details from the MBean
            node_name = AdminControl.getAttribute(mbean, 'nodeName')
            server_name = AdminControl.getAttribute(mbean, 'name')
            
            # Determine Server Type (Application Server vs Web Server)
            # WebServers have a specific processType or can be identified by the MBean type
            is_webserver = "type=WebServer" in mbean
            server_type = "IHS/WebServer" if is_webserver else "AppServer"

            # Get Host Name from AdminConfig
            node_id = AdminConfig.getid('/Node:' + node_name + '/')
            host_name = AdminConfig.showAttribute(node_id, 'hostName')
            
            # Get Software Version (WebSphere or IHS version)
            version = AdminControl.getAttribute(mbean, 'serverVersion')
            
            # Get Java Version (Only applicable to AppServers)
            java_version = "N/A"
            if not is_webserver:
                jvm_mbean = AdminControl.queryNames('type=JVM,node=' + node_name + ',process=' + server_name + ',*')
                if jvm_mbean:
                    java_version = AdminControl.invoke(jvm_mbean, 'getProperty', 'java.version')
                else:
                    java_version = "Unknown (Stopped)"

            # Print CSV Row
            print("%s,%s,%s,%s,%s,%s" % ( host_name, node_name,server_type, server_name, version, java_version))
            
        except Exception, e:
            # Silently skip items that cannot be queried (e.g., mid-restart)
            continue

if __name__ == "__main__":
    get_all_versions()
