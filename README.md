# labmgt

Some script(s) that I use for automating my homelab, these mainly suround power management and infrastructure management. I tend to write all my code in Python 3.x+, with a dusting of bash shell scripts, I prefer to run my Python apps in virtual envs, and recommend others do the same (with my code)

### Scripts

| Script | Purpose |
| --- | --- |
| pwrgmt.py | Provides power management for vSphere ESXi its, it was specifically written to use vSphere ESXi and APC PDU's.  <br>It uses the vCenter API to manage the host, and **telnet** is used to manage the PDU. |
| -   |     |
| -   |     |
| -   |     |

### Requirements

Docker or Python 3.x

### Installation


#### Local

- Clone the repository
- Install the necessary prerequisites

```
pip install -r requirements.txt
```

#### Docker

- Clone the repository
- Build the docker image

```
docker build -t nexus.prjx.uk/repository/main/labmgt .
```

- Note the Docker image will not run any command when started - You need to pass what command to run, such as:

```
docker run -ti --rm app/powrmgt.py host shutdown
docker run -ti --rm app/powrmgt.py host up
```

- It has been done this way, as the docker container only runs the script and then exits, the intent is, this is run via a Cron

## PwrMgt

#### Configuration

The script needs to know the details for your VMWare ESXi hosts and APC PDU, these are configured in the etc/config.yml file:

```YAML
## Login details and IP to access the PDU via telnet 
apc:
  password: apc
  server: 192.168.5.200
  username: apc

## Details for each ESXi host you want to manage, this includes if they are "enabled" (i.e. managed) and what PDU socket they are plugged into
hosts:
  esx-01.domain.com:
    enabled: false
    fqdn: esx-01.domain
    outlet: '5'
    web_ui: [https://esx-01.domain.com/ui/#/login](https://esx-01.domain.com/ui/#/login)
  esx-02.domain.com:
    enabled: false
    fqdn: esx-01.domain
    outlet: '4'
    web_ui: [https://esx-02.domain.com/ui/#/login](https://esx-02.domain.com/ui/#/login)
## Details for the vCenter, the API used to freeze and unfree
vcenter:
  username: [administrator@vsphere.local](mailto:administrator@vsphere.local) 
  password: password
  port: 443
  server: vcenter.domain

settings:
  ## Time between PDU power off, and PDU power on
  power_cycle_sleep: 10
  ## Time to wait before exiting maintenance mode - this much be sufficient for the ESXi to boot and notify vCenter it is available
  webui_check_sleep: 280
  ## The script can generate a lot of output, but this is useful for troubleshooting, but otherwise turn it off
  show_debug_output: true
```

Usage

Assumptions - You're ESXi hosts need to be configured as "Switch on when power restored", they are also connected to a smart APC PDU such as  APC AP7821B

| Command | Notes |
| --- | --- |
| shutdown | Will put the specified ESXi hosts in maintenance mode, then gracefully shutdown the node. Note, you should use DRS to ensure VMs are migrated other hosts.<br>**Example**:<br>pwrmgt.py host shutdown |
| up  | Will power-cycle the APC PDU, which restores power to the ESXi host causing it to boot up, it then waits a time (see <span style="color: #000080; font-weight: bold;">webui_check_sleep</span>) for the ESXi host to boot up, and then exits maintenance mode.<br>**Example**:<br>pwrmgt.py host up |
| pause | Puts the ESXi host into maintenance mode.<br>**Example**:<br>pwrmgt.py host pause |
| unpause | Exits maintenance mode.<br>**Example**:<br>pwrmgt.py host unpause. |