# Node Info

A lightweight Python web service that displays basic hardware and system info for the host node.  
Useful for Docker Swarm clusters — run in `global` mode to see per-node details behind Traefik or directly via port access.

## Features

- Plain text output (no HTML)
- CPU model, core and thread count
- Total and used memory
- Uptime
- Hostname and container ID
- Minimal footprint (~50 MB image)

## Example Output

```

Node: srv2
Platform: Linux-6.6.15-amd64-x86_64-with-glibc2.37
CPU model: AMD Ryzen 7 7840HS w/ Radeon 780M Graphics
CPU cores: 8
CPU threads: 16
Memory total: 31.36 GB
Memory used: 12.43 GB (39%)
Uptime: 3 days, 6:24:57
Container hostname: 1a2b3c4d5e6f

````

## Build and Run Locally

```bash
docker build -t nodeinfo .
docker run --rm -p 8080:8080 nodeinfo
curl http://localhost:8080
````

## Deploy in Docker Swarm

Example `hwinfo.yml`:

```yaml
version: "3.8"

services:
  hwinfo:
    image: ghcr.io/skjnldsv/docker-hwinfo:main

    networks: 
      - proxy
    ports:
      - 8080
     
    environment:
      NODE_HOSTNAME: "{{.Node.Hostname}}"

    healthcheck:
      test: ["CMD", "curl", "-f", "http://127.0.0.1:8080"]
      interval: 10s
      timeout: 10s
      retries: 5

    deploy:
      mode: global

      labels:
        traefik.enable: "true"
        traefik.http.routers.hwinfo.rule: Host(`hwinfo.domain.com`)
        traefik.http.routers.hwinfo.entrypoints: websecure
        traefik.http.routers.hwinfo.tls.certresolver: letsencryptresolver
        # fake value https://github.com/containous/traefik/issues/5732
        traefik.http.services.hwinfo.loadbalancer.server.port: 8080

networks:
  proxy:
    external: true

```
