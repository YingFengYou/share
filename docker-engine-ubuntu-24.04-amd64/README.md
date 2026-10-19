# Docker Engine for Ubuntu 24.04 (Noble) amd64

这是从 Docker 官方稳定仓库下载的 Ubuntu 24.04（Noble）amd64 离线安装包集合。

下载来源：<https://download.docker.com/linux/ubuntu/dists/noble/pool/stable/amd64/>

## 包含组件

- Docker Engine：`29.9.1`
- Docker CLI：`29.9.1`
- containerd.io：`2.4.2`
- Docker Buildx 插件：`0.38.0`
- Docker Compose 插件：`5.6.0`

## 校验

在当前目录执行：

```bash
sha256sum -c SHA256SUMS
```

`PACKAGE-METADATA.txt` 保存了每个包的官方仓库 URL、版本和 SHA-256 校验值。

## 安装

这些包适用于 Ubuntu 24.04 amd64。Docker 官方文档建议先确保系统已安装基础依赖，并移除可能冲突的发行版 Docker 包（如 `docker.io`、`containerd` 和 `runc`）。在当前目录执行：

```bash
sudo dpkg -i ./containerd.io_*.deb \
  ./docker-ce_*.deb \
  ./docker-ce-cli_*.deb \
  ./docker-buildx-plugin_*.deb \
  ./docker-compose-plugin_*.deb
```

如果 `dpkg` 报告缺少 Ubuntu 系统依赖，可执行：

```bash
sudo apt-get install -f
```

安装后检查服务：

```bash
sudo systemctl enable --now docker
sudo docker version
sudo docker compose version
sudo docker buildx version
```

Docker 官方 Ubuntu 安装文档：<https://docs.docker.com/engine/install/ubuntu/>

> 注意：这些是 amd64 包，不适用于 arm64、armhf、s390x 或 ppc64le。Docker Engine 及其依赖会安装系统服务，请在生产环境安装前检查防火墙和现有容器运行时配置。
