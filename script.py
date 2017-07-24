import sys
import ipaddress
import pexpect
import datetime

# Global variable that will store the VLAN from the command line argument, to be referenced by other functions
vlan = 0
failed = {}


def main():
    # Check if command line arguments are included, otherwise terminate the script
    if len(sys.argv) < 2:
        print("Usage: python3 " + sys.argv[0] + ' <file with IP addresses> <VLAN number>')
        return
    else:
        try:
            file = open(sys.argv[1], 'r')
        except IOError:
            print('Error opening ' + sys.argv[1] + ', either file does not exist or cannot be opened!')
            return

        # Access the global variable 'vlan' and assign a value to it
        global vlan
        vlan = sys.argv[2]

        # Create a dictionary to store {ip address : interface} values
        ip_dict = {}

        # Attempt to read each line in the txt file with IP addresses
        for line in file:
            # From left to right, save everything to 'ip' until a ',' is found, afterwhich everything is saved to the
            # 'interface' field
            try:
                ip, interface = line.split(',')
            except ValueError:
                print('Skipping ' + line.rstrip('\n') + ', invalid format')
                continue

            # Remove white spaces
            interface = interface.strip()

            # Ensure that IP address read from file is a valid IP address, otherwise skip it (using 'pass', to continue
            # reading through the rest of the file
            try:
                ipaddress.ip_address(ip)
            except ValueError:
                print("Invalid IP address:", ip)
                pass
            else:
                # If IP address is valid, add it to the list
                ip_dict[ip] = interface

        # Iterate through the list and run the 'run_cmds' function for each pair of IP address and interface
        for ip_add, vlan_int in ip_dict.items():
            ssh(ip_add, vlan_int)

        if len(failed) > 0:
            print('The following IP addresses failed and could not be processed: ')
            for add, msg in failed.items():
                print(add + ' - ' + '(' + msg + ')')


def ssh(ip_add, vlan_int):
    global vlan
    now = datetime.datetime.now()

    fout = open('logfile', 'a')
    fout.write('-----Begin log for ' + ip_add + ' at ' + now.strftime('%d/%m/%Y %H:%M:%S') + '-----\n')
    ssh_newkey = 'Are you sure you want to continue connecting'

    p = pexpect.spawnu('ssh cisco@' + ip_add)
    p.logfile_read = fout
    i = p.expect([ssh_newkey, 'Password:', 'cisco@', pexpect.TIMEOUT], timeout=6)

    if i == 0:
        print('[' + ip_add + '] ' + 'First time connecting to host, responding yes')
        p.sendline('yes')
        i = p.expect([ssh_newkey, 'Password:', 'cisco@', pexpect.EOF])
    if i == 3:
        failed[ip_add] = 'SSH connection failed'
        print('[' + ip_add + '] ' + 'SSH connection failed, skipping this IP address ...')
        now = datetime.datetime.now()
        fout.write('\n-----End log for ' + ip_add + ' at ' + now.strftime('%d/%m/%Y %H:%M:%S') + '-----\n\n')
        return
    if i == 2:
        print('[' + ip_add + '] ' + 'SSH password prompted')
        p.sendline('cisco')
        try:
            if p.expect('>', 2) == 0:
                print("[" + ip_add + "] SSH login successful")
        except pexpect.EOF:
            failed[ip_add] = 'Incorrect SSH password'
            print('[' + ip_add + '] Incorrect SSH password, skipping this IP address ... ')
            print('------------------------------------------------------')
            now = datetime.datetime.now()
            fout.write('\n-----End log for ' + ip_add + ' at ' + now.strftime('%d/%m/%Y %H:%M:%S') + '-----\n\n')
            return
    elif i == 1:
        p.sendline('cisco')

    p.sendline('enable')

    i = p.expect(['#', 'Password'])
    if i == 1:
        print('[' + ip_add + '] Enable password prompted')
        p.sendline('cisco')
        i = 0
    if i == 0:
        print('[' + ip_add + '] Successfully entered privileged mode')
    else:
        failed[ip_add] = 'Invalid enable password'
        print('[' + ip_add + '] Invalid enable password, skipping this IP address ... ')
        print('------------------------------------------------------')
        now = datetime.datetime.now()
        fout.write('\n-----End log for ' + ip_add + ' at ' + now.strftime('%d/%m/%Y %H:%M:%S') + '-----\n\n')
        return

    p.sendline('configure terminal')

    p.sendline('interface ' + vlan_int)
    i = p.expect(['config-if', '%'], timeout=0.5)
    if i == 0:
        print('[' + ip_add + '] Inside interface subconfiguration mode for ' + vlan_int)
    elif i == 1:
        failed[ip_add] = 'Could not access interface ' + vlan_int + ' on switch'
        print('[' + ip_add + '] Invalid interface ' + vlan_int + ' on switch, aborting ...')
        print('------------------------------------------------------')
        now = datetime.datetime.now()
        fout.write('\n-----End log for ' + ip_add + ' at ' + now.strftime('%d/%m/%Y %H:%M:%S') + '-----\n\n')
        return

    p.sendline('switchport access vlan ' + vlan)
    try:
        if p.expect('Access VLAN does not exist', timeout=0.5) == 0:
            print('[' + ip_add + '] VLAN does not exist, was created by switch')
            print('[' + ip_add + '] VLAN ' + vlan + ' assigned to interface ' + vlan_int)
    except:
        print('[' + ip_add + '] Interface ' + vlan_int + ' assigned to VLAN ' + vlan)

    print('------------------------------------------------------')
    now = datetime.datetime.now()
    fout.write('\n-----End log for ' + ip_add + ' at ' + now.strftime('%d/%m/%Y %H:%M:%S') + '-----\n\n')
    p.terminate()
    return


if __name__ == "__main__":
    main()