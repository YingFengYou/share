# Amazon Corretto 17 Alpine 3.24.1 X11 Secure

该目录用于从现有的 `amazoncorretto-17-alpine-3.24.1-x11-secure-v1` Docker archive 重打包镜像，同时更新 JDK 和 Alpine 安全包，并保留原有的 Alpine 3.24.1、OpenSSL 和 X11 安全层。

本次修复版本：

- Amazon Corretto JDK `17.0.21.1+2-LTS`（发行包 `17.0.21.1.2`）
- `musl` `1.2.6-r3`
- `musl-utils` `1.2.6-r3`
- `zlib` `1.3.2-r1`

这些 Alpine 包版本对应 `CVE-2026-107891`、`CVE-2026-85091` 在 Alpine 3.24 分支的官方修复版本。

## 构建

当前仓库发布的是 Docker `save` 归档。由于重打包不需要 Docker daemon，可在 Linux 环境执行：

```sh
python3 build-image.py \
  --base-archive /path/to/amazoncorretto-17-alpine-3.24.1-x11-secure.tar \
  --jdk-archive /path/to/amazon-corretto-17-x64-alpine-jdk.tar.gz \
  --apk /path/to/musl-1.2.6-r3.apk \
  --apk /path/to/musl-utils-1.2.6-r3.apk \
  --apk /path/to/zlib-1.3.2-r1.apk \
  --output amazoncorretto-17-alpine-3.24.1-x11-secure-v3.tar
```

AWS permanent URL：

`https://corretto.aws/downloads/latest/amazon-corretto-17-x64-alpine-jdk.tar.gz`

本次构建使用的 JDK SHA-256：

`fa46b3b71a1ae8d80c30787f242539a62c6db9a74c186fb15aef20db09a19dab`

输出归档架构保持为 `amd64`，镜像标签保持为 `amazoncorretto:17-alpine`。构建后应从归档内的 `usr/lib/jvm/default-jvm/release` 验证 JDK 版本，并从最终 `lib/apk/db/installed` 验证 Alpine 包版本。
