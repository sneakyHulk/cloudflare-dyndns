# cloudflare-dyndns

Middleware for updating [Cloudflare](https://www.cloudflare.com/) DNS records through an [AVM FRITZ!Box](https://en.avm.de/products/fritzbox/).

## Getting started

### Create a Cloudflare API token

Create a [Cloudflare API token](https://dash.cloudflare.com/profile/api-tokens) with **read permissions** for the scope `Zone.Zone` and **edit permissions** for the scope `Zone.DNS`.

![Create a Cloudflare custom token](./images/create-cloudflare-token.png "Create a Cloudflare custom token")

### :rocket: Self-host cloudflare-dyndns

#### Run on Docker

Start cloudflare-dyndns:

```bash
docker run -p 9017:80 ghcr.io/l480/cloudflare-dyndns:latest
```

Or start with docker-compose:

```

services:
  dyndns:
    container_name: dyndns
    image: ghcr.io/sneakyhulk/cloudflare-dyndns:latest
    hostname: dyndns
    restart: unless-stopped
    ports:
      - 9017:80
```

The update URL for the FRITZ!Box results to:

```
http://<server host name or ip address>:9017?token=<pass>&zone=<zone>&record=<username>&ipv4=<ipaddr>&ipv6=<ip6addr>
```
