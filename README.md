# Pre-Requisites  

Please be sure you have installed:  
  - vagrant  
  - virtualbox (vagrant provisioner)
  - ansible (pip install ansible==2.1.0.0)  


# Quick start  

`chmod 400 synced_folder/vagrant_rsa`  
`vagrant up`  
`ansible-playbook -i inventory consul.yml`  

go to http://192.168.10.10:8500/ui  


# Description

Manage Consul Agents on hosts.  
See more about Consul on Hashicorp official documentation : http://consul.io

"impact" on the node running the agent is :  
  - 1 service : `/etc/init.d/consul`    (deamon manager : start, restart, stop)
  - 1 binary : `/usr/local/bin/consul`  (hashicorp download: https://www.consul.io/downloads.html)
  - 3 directories :
    - config: `/etc/consul.d/`
    - data:   `/root/consul_data/`
    - logs:   `/var/log/consul/`

Synchronization mecanism is handled with files in config folder `/etc/consul.d/` :  
  - python sync script: `scripts/synchronize.py`  
  - python sync config: `scripts/synchronize.cfg`  
  - python  virtualenv: `venv_python`  
  - watcher definition: `watch_service_definition.json`  
    - watch the service definition on KV store (catalog)  
    - trigger the sync script when value changes  

When agent starts, the watcher is triggered automatically (default consul lifecycle).  
So, at first install, the sync script is called:  
  - download the service definition from kv catalog (WARNING)   
  - sync local definitions in `config` folder.  

After restart, all JSON files (service, checks) will be used by consul agent.  

## WARNING : Before installing an agent for managing a service, the service definition must exists on catalog.  

From this YAML service definition `templates/definitions/services/specific/openstack/keystone`...  
```
---

service:
  name: keystone
  port: 5000
  tags:
    - identity
  checks:
    - id: tcp_localhost_22
      name: TCP on port 22
      tcp: localhost:22
      interval: 5s
      timeout: 3s
    - id: tcp_localhost_80
      name: TCP on port 80
      tcp: localhost:80
      interval: 5s
      timeout: 3s
    - id: bash_check_disks
      name: Disk utilization
      script: df -PH
      interval: 5s
      timeout: 3s

```

... this JSON value will be PUT on catalog: `/kv/definitions/services/keystone`  

```
{
    "service": {
        "name": "keystone",
        "port": 5000,
        "tags": [
            "identity"
        ],
        "checks": [
            {
                "id": "tcp_localhost_22",
                "interval": "5s",
                "name": "TCP on port 22",
                "tcp": "localhost:22",
                "timeout": "3s"
            },
            {
                "id": "tcp_localhost_80",
                "interval": "5s",
                "name": "TCP on port 80",
                "tcp": "localhost:80",
                "timeout": "3s"
            },
            {
                "id": "bash_check_disks",
                "interval": "5s",
                "name": "Disk utilization",
                "script": "df -PH",
                "timeout": "3s"
            }
        ]
    }
}
```

Some files will be created in `/etc/consul.d/` folder:  

```
consul.d/
|-- check_bash_check_disks.json
|-- check_tcp_localhost_22.json
|-- check_tcp_localhost_80.json
|-- scripts
|   |-- synchronize.cfg
|   `-- synchronize.py
|-- service_keystone.json
`-- watch_service_definition.json
```

  - All checks are stored as seperated files.  
  - Each one contain only one check definition.  
  - ***id*** field is used to create the filename `check_{{ id }}.json`:  

For example, `check_bash_check_disks.json` contains:  

```
{
    "check": {
        "id": "bash_check_disks",
        "interval": "5s",
        "name": "Disk utilization",
        "script": "df -PH",
        "timeout": "3s"
    }
}

```

  - ***name*** is used to create service definition filename `service_{{ name }}.json`:  

`service_keystone.json` contains only the service, not the checks:  

```
{
    "service": {
        "name": "keystone",
        "port": 5000,
        "tags": [
            "identity"
        ]
    }
}

```


# Variables

If you don't specify anything, consul agent will run with **server** option.  
Moreover, the agent will define the node as member of **consul** service.  
It means that the node will be configured with **default consul service definition**.  
You can find this definition at : `templates/definitions/consul`  

As consul act as a service, you cannot override `/etc/init.d/consul` daemon installation path.
Else, you can override following default variables when applying the role on hosts:

```
# consul binary
hashicorp_base_url: https://releases.hashicorp.com/consul
operating_system: linux
architecture: amd64
version: 0.6.3

# directories
bin_dir: /usr/local/bin
config_dir: /etc/consul.d
data_dir: /root/consul_data
logs_dir: /var/log/consul

# consul config
web_ui_port: 8500    # TODO: be able to run the server on any port (bugfix some tasks)
catalog_version: v1

# options
mode: server
service_name: consul
force: no
```

`force` : This variable will make the role doing some actions even if everything looks already ok:  
  - reinstall the hashicorp binary
  - remove existing service definition (`/etc/consul.d/service_definition_{{ service_name }}.json`)

And the role will also launch some specific tasks, like:
  - route DNS

How to set it ??  

  - you can set this variable to `yes` in the playbook.  

  ```
  - hosts: consul-servers
    become: yes
    roles:
      - role: consul
        force: yes
  ```

  - you can override when running you command:  

`ansible-playbook -i inventory consul.yml --extra-vars "force=True"`  


So, be careful when using the force method, you should couple the force mode to a specific tag...
For example, if you just want to reinstall consul binary, you could run a command like this:  

`ansible-playbook -i inventory consul.yml --tags consul-binary --extra-vars "force=True"`  



# Playbook

The project contains a sample :  

```
- hosts: consul-servers
  become: yes
  roles:
    - role: consul
      force: no

#---------------------------------------
# Consul Clients
#---------------------------------------

- hosts: consul-services
  become: yes
  roles:
    - role: consul
      service_name: "{{ inventory_service_name }}"
      mode: client
      force: yes
```


# Inventory

A specific variable `inventory_service_name` specifies the service that the host represents.   
You must specify it if not running default mode (server) which automatically will use **consul** for service name.    


```
[consul-server-nodes]
server1           ansible_ssh_host=192.168.10.10

[api]
consul-client-1   ansible_ssh_host=192.168.10.21  inventory_service_name=api
```
