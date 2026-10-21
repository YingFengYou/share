# 镜像构建与发布记忆

## Alpine + Nginx 镜像方案

当需要发布 Alpine 3.24.1 + Nginx 镜像时，默认使用 **linux/amd64**，不要发布 ARM 镜像。

### 优先方案

1. 优先从 Docker Hub 使用官方 Nginx 镜像，不从头构建 Nginx：
   - `docker.io/library/nginx:1.30.4-alpine3.24-slim`
2. 拉取时显式指定架构：
   ```bash
   podman pull --platform linux/amd64 docker.io/library/nginx:1.30.4-alpine3.24-slim
   ```
3. 必须实际核对架构和 Alpine 版本，不能只相信 tag：
   ```bash
   podman image inspect IMAGE --format '{{.Architecture}} {{.Os}}'
   podman run --rm --network host --platform linux/amd64 IMAGE cat /etc/alpine-release
   ```
4. 以官方镜像为基础，仅升级触发 High/Critical 漏洞的安全包，避免执行整套 `apk upgrade` 导致 Alpine 从 3.24.1 变成 3.24.2。例如当前方案：
   ```dockerfile
   FROM docker.io/library/nginx:1.30.4-alpine3.24-slim
   RUN apk add --no-cache --upgrade pcre2
   ```

### 构建与验证

- ARM64 主机上构建 amd64 时使用 `--platform linux/amd64`，并确保 QEMU/binfmt 已启用。
- Podman Sandbox 网络通常使用 `--network host`，否则可能受 iptables/netavark 限制。
- 运行验证：`nginx -t`，并请求 HTTP 端口确认返回 200。
- 导出 Docker archive 和 OCI archive，并为每个归档生成 SHA256 校验文件。

### 安全门禁

使用 Trivy 扫描 Docker archive：

```bash
trivy image --input IMAGE.tar --scanners vuln --severity HIGH,CRITICAL
```

只有 `HIGH=0` 且 `CRITICAL=0` 才允许提交和发布。扫描时记录 Trivy 版本、目标镜像、Alpine 版本和完整 JSON 报告。

### GitHub 发布

- 将 Dockerfile、README、镜像归档、校验文件和 Trivy 报告提交到 `YingFengYou/share`。
- Release tag 使用明确架构名，例如 `v3.24.1-nginx-amd64`。
- Release 上传 Docker/OCI 归档、对应 SHA256 文件和扫描报告。
- 如果之前发布过 ARM 版本且用户无法使用 ARM，应删除旧 ARM Release/tag，避免误下载。
