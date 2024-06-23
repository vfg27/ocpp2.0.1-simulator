import yaml
import subprocess

CONFIG_FILE = 'charging/server_config.yaml'
EXECUTE_FILE = 'charging/server/'
SECURITY_PROFILE = 1

# Open server config file
with open(CONFIG_FILE, "r") as file: 
    try:
        # Parse YAML content
        content = yaml.safe_load(file)

        if "version" in content:
            VERSION = content["version"]

        # Set accepted tokens
        if "security" in content:
            if "profile" in content["security"]:
                SECURITY_PROFILE = content["security"]["profile"]
        
        EXECUTE_FILE = EXECUTE_FILE + VERSION + "/server" + str(SECURITY_PROFILE) + '.py'
        subprocess.run(["python3", EXECUTE_FILE])

    except yaml.YAMLError as e:
        print('Failed to parse server_config.yaml')
