### CPOC Software Programmability Project
### Q4 FY17
### Contributors: 
### Ajay Doshi (ajdoshi@cisco.com)
### Megha Chaudhary (megch@cisco.com)

To run the script, 2 modules need to be installed, namely pexpect and ipaddress  
   If the script fails to run (ImportError: no module named pexpect/ipaddress), simply run the 2 commands below:

```
sudo pip install pexpect
sudo pip install ipaddress
```   
To run the script, use the following format:

```
python3 script.py <text file with IP addresses> <VLAN number>
```

The script terminates if one or both of the command line arguments (enclosed in <>) are missing

Example usage with files in this repo:

```
python3 script.py test.txt 123
```

Note: The script assumes that all passwords such as SSH and privilege mode are set to *cisco*
