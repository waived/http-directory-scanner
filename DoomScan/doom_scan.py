#!/usr/bin/env python3
import sys
import os
import random
import threading
import requests
from urllib.parse import urlparse

_proxies = []
_results = []

_active = 0

def scan(domain, path, wait):
    global _proxies, _active
    
    _active +=1
    
    # pull random socks4 proxy to use
    proxy_ip, proxy_port = random.choice(_proxies).split(":")
    
    # remove any leading forward-slash
    path = path.lstrip("/")
    
    # format target url
    url = f"http://{domain}/{path}"
    
    # set proxy
    proxies = {
        'http': f'socks4://{proxy_ip}:{proxy_port}',
        'https': f'socks4://{proxy_ip}:{proxy_port}',
    }
    
    # send http-head probe
    try:
        response = requests.head(url, proxies=proxies, timeout=wait)
    
        if response.status_code == 200:
            _results.append(url)

    #except requests.RequestException:
    #    pass
    except Exception as e:
        print(e)
    
    _active -=1

def rslv(_site):
    _host = _site
    if not (_host.lower().startswith('http://') or _host.lower().startswith('https://')):
        _host = 'http://' + _host
    try:
        _domain = urlparse(_host).netloc
        
        return _domain
    except:
        sys.exit('\r\nDNS resolution error! Exiting...\r\n')

def main():
    global _active, _results, _proxies
    
    # clear terminal env
    if sys.platform == 'win32':
        os.system('cls')
    else:
        os.system('clear')
    
    # display banner
    print('''
       ██                                                                  
      ╔██                                                                  
  ███████  ╔██████   ╔██████  ╔██████████   ╔██████  ╔█████   ╔██████   ╔███████ 
╔██═══╗██ ╔██═══╗██ ╔██═══╗██ ╚╗██═╗██═╗██ ╔██╔═══╝ ╔██══╗██  ╚════╗██  ╚╗██══╗██
║██╔██║██ ║██╔██║██ ║██╔██║██  ║██ ║██ ║██ ╚╗█████  ║██  ╚═╝  ╔███████   ║██  ║██
║██╚═╝║██ ║██╚═╝║██ ║██╚═╝║██  ║██ ║██ ║██  ╚════██ ║██  ╔██ ╔██═══╗██   ║██  ║██
╚╗███████ ╚╗██████╝ ╚╗██████╝ ╔███ ║██ ║██ ╔██████╝ ╚╗█████╝ ╚╗████████ ╔███  ║██
 ╚══════╝  ╚═════╝   ╚═════╝  ╚══╝ ╚═╝ ╚═╝ ╚═════╝   ╚════╝   ╚═══════╝ ╚══╝  ╚═╝           
 
               A lightweight HTTP site-mapper / directory scanner
 
''')
    _dirs = [] # holds collection to directories
    tasks = [] # holds collection to all threads
    
    # capture user input
    try:
        _site = input('Enter domain/URL: ')
        
        # domain resolution
        _site = rslv(_site)
        
        _prox = input('SOCKS4 list: ')
        
        if not os.path.exists(_prox):
            sys.exit('\r\nError! File not found...\r\n')
        else:
            # add proxies to list
            with open(_prox, "r") as f:
                for line in f:
                    if "\n" in line:
                        # remove any carriage return/s
                        line = line.replace("\n", "")
                        _proxies.append(line)
                    else:
                        _proxies.append(line)
            
        _path = input('Directory list: ')
        
        if not os.path.exists(_path):
            sys.exit('\r\nError! File not found...\r\n')
        else:
            # add directories to list
            with open(_path, "r") as f:
                for line in f:
                    if "\n" in line:
                        # remove any carriage return/s
                        line = line.replace("\n", "")
                        _dirs.append(line)
                    else:
                        _dirs.append(line)
            
        _thdz = int(input('Thread/s (default 10): '))
        
        _wait = int(input('Timeout in seconds: '))
        
        input('\r\nReady? Strike <ENTER> to launch...')
            
    except KeyboardInterrupt:
        sys.exit()
    except:
        main()

    # begin scan
    print('\r\nNow scanning! Results posted at end. Strike <CTRL+C> to abort...')

    # iterate through dir list
    try:
        for _dir in _dirs:
            # wait for thread-cap
            while _active > _thdz:
                # thread-lock would be more cpu friendly, but im lame
                pass
            
            # send out probe
            x = threading.Thread(target=scan, args=(_site, _dir, _wait))
            tasks.append(x)
            x.start()
    except KeyboardInterrupt:
        sys.exit('\r\nAborted!\r\n')
    except Exception as e:
        sys.exit(e)
        
    #finish up
    if not _results:
        sys.exit('\r\nNothing found during scan! Exiting...\r\n')
    else:
        print('Results:\r\n=============\r\n')
        i = 0
        for _result in _results:
            i +=1
            
            print(f'[Entry #{i}] {_result}')

    sys.exit()

if __name__ == '__main__':
    main()
