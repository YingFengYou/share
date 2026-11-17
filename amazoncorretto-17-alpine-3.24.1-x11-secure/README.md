# Amazon Corretto 17 Alpine 3.24.1 X11 Secure

该目录用于从现有的 `amazoncorretto-17-alpine-3.24.1-x11-secure-v1` Docker archive 重打包镜像，仅替换 JDK 层，保留原有的 Alpine 3.24.1、OpenSSL 和 X11 安全更新层。

当前镜像中的 JDK 为 `17.0.19+10-LTS`。升级目标为 Amazon Corretto `17.0.21+11-LTS`，对应官方发行包 `17.0.21.0.11`。

## 构建

当前仓库发布的是 Docker `save` 归档。由于重打包不需要 Docker daemon，可在 Linux 环境执行：

```sh
python3 build-image.py \
  --base-archive /path/to/amazoncorretto-17-alpine-3.24.1-x11-secure.tar \
  --jdk-archive /path/to/amazon-corretto-17.0.21.0.11-alpine-linux-x64.tar.gz \
  --output amazoncorretto-17-alpine-3.24.1-x11-secure-jdk17.0.21.tar
```

官方 JDK 包下载地址：

`https://corretto.aws/downloads/resources/17.0.21.0.11/amazon-corretto-17.0.21.0.11-alpine-linux-x64.tar.gz`

官方 SHA-256：

`0c457166868cba83eb81c48facdc3dede3e0c78d76bbdcd83ad69b966f5280b2`

输出归档的架构保持为 `amd64`，镜像标签保持为 `amazoncorretto:17-alpine`。构建后应从归档内的 `usr/lib/jvm/default-jvm/release` 验证 `JAVA_VERSION="17.0.21"`。
