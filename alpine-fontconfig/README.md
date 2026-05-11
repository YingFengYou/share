# Alpine fontconfig 离线安装指南

本目录包含了 Alpine Linux v3.20 (x86_64) 系统下 `fontconfig` 及其所有必要的依赖包。

## 包含的软件包

| 软件包名称 | 版本 | 说明 |
| :--- | :--- | :--- |
| `fontconfig` | 2.15.0-r1 | 字体配置库 |
| `libexpat` | 2.7.5-r0 | XML 解析库 (fontconfig 依赖) |
| `freetype` | 2.13.2-r0 | 字体渲染引擎 (fontconfig 依赖) |
| `musl` | 1.2.5-r3 | 标准 C 库 |
| `zlib` | 1.3.2-r0 | 压缩库 |
| `libpng` | 1.6.57-r0 | PNG 图像库 |
| `brotli-libs` | 1.1.0-r2 | Brotli 压缩库 |
| `libbz2` | 1.0.8-r6 | Bzip2 压缩库 |

## Dockerfile 使用示例

您可以将这些 `.apk` 文件复制到镜像中，并使用 `apk add --allow-untrusted` 进行本地安装。

```dockerfile
FROM alpine:3.20

# 创建临时目录存放安装包
RUN mkdir -p /tmp/pkgs

# 将所有下载的 apk 文件拷贝到镜像内
COPY *.apk /tmp/pkgs/

# 本地安装所有包
# --allow-untrusted 是因为本地文件没有经过远程仓库的签名验证
RUN apk add --no-cache --allow-untrusted /tmp/pkgs/*.apk \
    && rm -rf /tmp/pkgs

# 验证安装
RUN fc-cache --version
```

## 注意事项
1. **架构匹配**：这些包是为 `x86_64` 架构下载的。如果您的基础镜像是 `arm64`，请告知我重新下载。
2. **版本匹配**：这些包对应 Alpine `v3.20`。建议基础镜像也使用 `FROM alpine:3.20` 以确保兼容性。
