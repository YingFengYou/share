ARG OPENSEARCH_VERSION=3.9.0
FROM opensearchproject/opensearch:${OPENSEARCH_VERSION}

USER root

# The official image already ships opensearch-knn in the 3.9.0 distribution.
# Install only the two optional language analyzers; fail if any requested plugin
# is missing after installation.
RUN set -eux; \
    /usr/share/opensearch/bin/opensearch-plugin list | grep -qx 'opensearch-knn' || \
      /usr/share/opensearch/bin/opensearch-plugin install --batch opensearch-knn; \
    /usr/share/opensearch/bin/opensearch-plugin install --batch analysis-smartcn; \
    /usr/share/opensearch/bin/opensearch-plugin install --batch analysis-nori; \
    /usr/share/opensearch/bin/opensearch-plugin list | grep -qx 'opensearch-knn'; \
    /usr/share/opensearch/bin/opensearch-plugin list | grep -qx 'analysis-smartcn'; \
    /usr/share/opensearch/bin/opensearch-plugin list | grep -qx 'analysis-nori'

USER opensearch
