# SSH Access

This document shows example access patterns for a private GangaCloud Data Engineering Workspace VM.

## Example Workspace VM

- VM name: `gc-de-workspace-001`
- Private IP: `10.10.0.103`
- Operating system: Ubuntu 24.04

## SSH ProxyJump Pattern

Use a bastion host to reach the private workspace VM:

```bash
ssh -J ubuntu@bastion.example.com ubuntu@10.10.0.103
```

With an SSH key:

```bash
ssh -i ~/.ssh/gangacloud-demo.pem -J ubuntu@bastion.example.com ubuntu@10.10.0.103
```

Optional `~/.ssh/config` entry:

```sshconfig
Host gc-de-workspace-001
    HostName 10.10.0.103
    User ubuntu
    ProxyJump ubuntu@bastion.example.com
    IdentityFile ~/.ssh/gangacloud-demo.pem
```

Then connect with:

```bash
ssh gc-de-workspace-001
```

## Copy Files with scp Through ProxyJump

Copy the demo repo to the private VM:

```bash
scp -r -o ProxyJump=ubuntu@bastion.example.com . ubuntu@10.10.0.103:~/gangacloud-customer-data-engineering-demo
```

Copy a file back from the private VM:

```bash
scp -o ProxyJump=ubuntu@bastion.example.com ubuntu@10.10.0.103:~/gangacloud-customer-data-engineering-demo/data/input/orders.csv .
```

## JupyterLab Through an SSH Tunnel

Start JupyterLab on the private VM:

```bash
cd ~/gangacloud-customer-data-engineering-demo
make setup
.venv/bin/jupyter lab --no-browser --ip 127.0.0.1 --port 8888
```

Create the tunnel from your local machine:

```bash
ssh -L 8888:127.0.0.1:8888 -J ubuntu@bastion.example.com ubuntu@10.10.0.103
```

Then open the JupyterLab URL shown by the server in your local browser.

## Limitations

- Hostnames, usernames, keys, and bastion addresses are examples.
- This demo assumes the VM already has Python, Java, and network access for package installation.
- The workspace VM is private and reached through a bastion or equivalent SSH gateway.
- This milestone does not include Docker, MinIO, PostgreSQL, Airflow, Kubernetes, FastAPI, or control-plane integration.
