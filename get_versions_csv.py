# Check Version CSV
# ./wsadmin.sh -lang jython -f /path/to/script/check_versions_csv.py > inventory.csv
# ./wsadmin.sh -lang jython -f /path/to/script/check_versions_csv.py -user <username> -password <password>
# ./wsadmin.sh -lang jython -user wasadmin -password web1sphere -f /tmp/check_versions_csv.py > inventory.csv
import sys
import re

def get_best_java_version(jvm_mbean):
    """
    Queries JVM properties and extracts version + patch for any Java version (8, 11, 17, 21+).
    """
    try:
        # We query these three properties as they cover almost all IBM/Oracle/OpenJDK scenarios
        rt_ver = AdminControl.invoke(jvm_mbean, 'getProperty', 'java.runtime.version')
        std_ver = AdminControl.invoke(jvm_mbean, 'getProperty', 'java.version')
        full_ver = AdminControl.invoke(jvm_mbean, 'getProperty', 'java.fullversion')
        
        combined = "|".join([rt_ver, std_ver, full_ver])
        
        # This regex looks for: 1.8.<patch> / 11.y.z / 21.y.z / IBM format 8.x.y.z
        match = re.search(r'([0-9]+(\.[0-9]+)+(_[0-9]+|[\+][0-9]+|-[a-zA-Z0-9]+)?)', combined)
        
        if match:
            return match.group(1)
        return std_ver.split()[0] # Fallback to first word of java.version
    except:
        return "Unknown"

def get_inventory():
    print("Hostname,NodeName,Java Version,WAS Version")

    nodes = AdminConfig.list('Node').splitlines()

    for node in nodes:
        node_name = AdminConfig.showAttribute(node, 'name')
        host_name = AdminConfig.showAttribute(node, 'hostName')

        # Locate a running server/nodeagent to query live MBeans
        server_mbean = AdminControl.queryNames('type=Server,node=' + node_name + ',process=nodeagent,*')
        if not server_mbean:
            others = AdminControl.queryNames('type=Server,node=' + node_name + ',*').splitlines()
            if others: server_mbean = others[0]

        if server_mbean:
            try:
                # WebSphere Version (Clean)
                raw_was = AdminControl.getAttribute(server_mbean, 'serverVersion')
                was_match = re.search(r'([0-9]+(\.[0-9]+)+)', raw_was)
                was_ver = was_match.group(1) if was_match else raw_was.split()[0]

                # Java Version (Clean + Patch)
                s_name = AdminControl.getAttribute(server_mbean, 'name')
                jvm_mbean = AdminControl.queryNames('type=JVM,node=' + node_name + ',process=' + s_name + ',*')
                
                java_ver = get_best_java_version(jvm_mbean) if jvm_mbean else "N/A"

                print("%s,%s,%s,%s" % (host_name, node_name, java_ver, was_ver))
            except:
                print("%s,%s,Error,Error" % (host_name, node_name))
        else:
            print("%s,%s,Node Agent Stopped,N/A" % (host_name, node_name))

if __name__ == "__main__":
    get_inventory()

