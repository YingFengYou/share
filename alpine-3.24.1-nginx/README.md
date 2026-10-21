# Nginx 1.30.4 on Alpine 3.24.1 (amd64)

这是从 Docker Hub 官方镜像 `nginx:1.30.4-alpine3.24-slim` 下载并基于其制作的安全更新镜像，目标平台为 `linux/amd64`。

## 镜像信息

- 官方基础镜像：`docker.io/library/nginx:1.30.4-alpine3.24-slim`
- Alpine：`3.24.1`
- Nginx：`1.30.4`
- 架构：`linux/amd64`
- 镜像 ID：`sha256:fe61d8952d09ca2db4705396235e98a25cb562d163c15b616d5c465edddac982`
- 端口：`80`

构建仅升级了 `pcre2` 安全包，保留官方 Nginx 的 entrypoint、配置和运行方式。

## 加载和运行

```bash
docker load -i nginx-1.30.4-alpine3.24-slim-secure-amd64.docker.tar
docker run --rm -p 8080:80 nginx:1.30.4-alpine3.24-slim-secure
```

Podman 用户也可以加载 OCI 归档：

```bash
podman load -i nginx-1.30.4-alpine3.24-slim-secure-amd64.oci.tar
```

## 漏洞扫描

使用 Trivy `0.76.0` 扫描镜像归档：

- High：`0`
- Critical：`0`
- Medium：`1`
- 扫描目标：`nginx-1.30.4-alpine3.24-slim-secure-amd64.docker.tar`

对应的完整 JSON 报告和 SHA256 校验文件也包含在目录和 Release 中。
