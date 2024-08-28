import paramiko
import tomli
import argparse
import os

def main():
    p = argparse.ArgumentParser('Script runner', description='It\'s a local script runner for ssh')
    p.add_argument('scriptFile', type=str, help='The script file to run')
    p.add_argument('-c','--config' , type=str, help='The config file for connect to the session', required=False, default='./config.toml')
    p.add_argument('arguments', type=str, nargs='*', help='The arguments for the script', default=[])
    args = p.parse_args()
    
    if not os.path.exists(args.config): 
        print(f'The config file ({args.config}) does not exist')
        return False
    
    with open(args.config, 'rb') as configFile:
        try:
            config = tomli.load(configFile)
        except tomli.TOMLDecodeError as e:
            print(f'TOMLDecodeError: {e}')
            return False
            
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname=config.get('host').get('ip'), username=config.get('host').get('username'), password=config.get('host').get('password'))
    except Exception as e:
        print(e)
        return False
    
    try:
        sftp = client.open_sftp()
        remote_path = f'/home/{config.get("host").get("username")}/s'
        sftp.put(args.scriptFile, remote_path)
        sftp.close()
    except Exception as e:
        print(f'SFTP Error: {e}')
        client.close()
        return False
    
    commands = [
        f'chmod +x {remote_path}',
        remote_path + ' ' + ' '.join(args.arguments),
        f'rm {remote_path}'
    ]


    for command in commands:
        _, stdout, stderr = client.exec_command(command)
        if commands.index(commands[1]) == 1:
            print(stdout.read().decode() + stderr.read().decode())
        
    client.close() 
    
if __name__ == '__main__':
    main()