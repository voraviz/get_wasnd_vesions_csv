# Check Version CSV
# ./wsadmin.sh -lang jython -f /path/to/script/check_versions_csv.py > inventory.csv
# ./wsadmin.sh -lang jython -f /path/to/script/check_versions_csv.py -user <username> -password <password>
import sys

def get_versions():
    # Header for the CSV output
    print("Hostname,NodeName,Java Version,WAS Version")

    # Get all running Server MBeans in the cell
    servers = AdminControl.queryNames('type=Server,*').splitlines()

    for server_mbean in servers:
        try:
            # Extract names from the live MBean
            node_name = AdminControl.getAttribute(server_mbean, 'nodeName')
            server_name = AdminControl.getAttribute(server_mbean, 'name')
            
            # 1. Get Host Name from AdminConfig for the specific node
            node_id = AdminConfig.getid('/Node:' + node_name + '/')
            host_name = AdminConfig.showAttribute(node_id, 'hostName')
            
            # 2. Get WebSphere Version
            was_version = AdminControl.getAttribute(server_mbean, 'serverVersion')
            
            # 3. Get Java Version from the associated JVM MBean
            jvm_mbean = AdminControl.queryNames('type=JVM,node=' + node_name + ',process=' + server_name + ',*')
            if jvm_mbean:
                java_version = AdminControl.invoke(jvm_mbean, 'getProperty', 'java.version')
            else:
                java_version = "Unknown"

            # Print in CSV format
            print("%s,%s,%s,%s" % (host_name, node_name, java_version, was_version))
            
        except Exception, e:
            continue

if __name__ == "__main__":
    get_versions()

