# OpenSearch 3.9.0 with k-NN, SmartCN and Nori

This directory builds a custom image from the official `opensearchproject/opensearch:3.9.0` image.

Preinstalled plugins:

- `opensearch-knn`
- `analysis-smartcn`
- `analysis-nori`

The GitHub Actions workflow builds an `amd64` image, verifies the installed plugin list, pushes the image to GHCR, and attaches an OCI image archive to the GitHub Release.

## Use the published image

```bash
docker pull ghcr.io/yingfengyou/opensearch:3.9.0-knn-smartcn-nori

docker run -d --name opensearch \
  -p 9200:9200 -p 9600:9600 \
  -e 'discovery.type=single-node' \
  -e 'OPENSEARCH_INITIAL_ADMIN_PASSWORD=ChangeThisToAStrongPassword!' \
  ghcr.io/yingfengyou/opensearch:3.9.0-knn-smartcn-nori
```

The tag is pinned to OpenSearch 3.9.0. OpenSearch 2.12 and later require a custom initial admin password when using the demo security configuration.

## Build locally

```bash
docker build --pull \
  --build-arg OPENSEARCH_VERSION=3.9.0 \
  -t opensearch:3.9.0-knn-smartcn-nori .
```

Official references: [OpenSearch downloads](https://opensearch.org/downloads/), [Docker installation](https://docs.opensearch.org/latest/install-and-configure/install-opensearch/docker/), and [plugin management](https://docs.opensearch.org/latest/install-and-configure/plugins/).
