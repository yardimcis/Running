

class engine():

    network_file_path = '/opt/Engine/Settings/Network.xml'
    environment_file_path = '/opt/Engine/Settings/Environment.xml'
    version = get_version()
    
    def __init__(self):
        Network_file = ET.parse(network_file_path)
        Environment_file = ET.parse(environment_file_path)
        N_root = Network_file.getroot()
        E_root = Environment_file.getroot()
    
    def get_version(self):
        version = subprocess.check_output(['uname', '-r'])
        if version == "4.0.8-v7\n":
            return 0
        elif version == "4.4.9-v7+\n":
            return 1

    def get_serial_ID(self, version):
        if version == 0:
            return N_root[0][1].find('CustomerID').text + N_root[0][1].find('DeviceID').text
        elif version == 1:
            return E_root[0][7].find('CustomerID').text + E_root[0][7].find('DeviceID').text
    
    def 
