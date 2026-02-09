# WebSphere ND configuration

Get all WebSphere online nodes from Deployment Manager with wsadmin and [Jython script](get_versions_csv.py) in CSV format

```bash
./wsadmin.sh -lang jython -f check_versions_csv.py > inventory.csv
```