# WebSphere ND configuration

Get all WebSphere online nodes from Deployment Manager with wsadmin and [Jython script](get_versions_csv.py) in CSV format

```bash
./wsadmin.sh -lang jython -f /path/to/script/check_versions_csv.py -user <username> -password <password>
```