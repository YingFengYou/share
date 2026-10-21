# Alpine 3.24.1 + Nginx

ARM64 OCI/Docker image built from `alpine:3.24.1` with Nginx installed from the Alpine 3.24 repository.

## Image details

- Base image: `alpine:3.24.1`
- Nginx: `1.30.4-r1`
- Architecture: `linux/arm64`
- Image ID: `sha256:28109a8db9a5aeb0e085b54ec064294e02206efdccd29c265bd3e3badb4d64e1`
- Default command: `nginx -g 'daemon off;'`
- Port: `80`

The build runs `apk upgrade --no-cache` before installing Nginx so that security updates available in the Alpine 3.24 repository are included while retaining the Alpine 3.24.1 base image lineage.

## Load and run

```bash
docker load -i alpine-3.24.1-nginx-arm64.docker.tar
docker run --rm -p 8080:80 alpine:3.24.1-nginx
```

For Podman, the OCI archive is also provided:

```bash
podman load -i alpine-3.24.1-nginx-arm64.oci.tar
```

## Vulnerability scan

Scanned with Trivy `0.76.0` using the vulnerability database available at build time.

- High: `0`
- Critical: `0`
- Scan target: `alpine-3.24.1-nginx-arm64.docker.tar`
- Report: `trivy-report.json`

Checksums are provided in the corresponding `.sha256` files.
