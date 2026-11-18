#!/usr/bin/env python3
"""Replace the Corretto JDK and selected Alpine security packages.

The input archive is the existing X11-secure image. Existing Alpine,
OpenSSL and X11 layers are retained byte-for-byte; the JDK layer is rebuilt
and an additional APK overlay carries the selected security updates.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import tarfile
import tempfile
from pathlib import Path

JDK_PATH = "usr/lib/jvm/java-17-amazon-corretto"
EXCLUDED_PREFIXES = ("usr/lib/jvm/",)
EXCLUDED_BINARIES = {
    "java", "javac", "jar", "jarsigner", "javadoc", "javap", "jcmd", "jconsole",
    "jdb", "jdeprscan", "jdeps", "jfr", "jhsdb", "jimage", "jinfo", "jlink",
    "jmap", "jmod", "jpackage", "jps", "jrunscript", "jshell", "jstack", "jstat",
    "jstatd", "keytool", "rmiregistry", "serialver",
}
APK_METADATA = {".PKGINFO", ".SIGN.RSA.alpine-devel@lists.alpinelinux.org-6165ee59.rsa.pub"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def add_fs_tree(out: tarfile.TarFile, source: Path, arc_root: str) -> None:
    for path in sorted(source.rglob("*")):
        rel = path.relative_to(source).as_posix()
        out.add(path, arcname=f"{arc_root}/{rel}", recursive=False)


def add_symlink(out: tarfile.TarFile, name: str, target: str) -> None:
    info = tarfile.TarInfo(name)
    info.type = tarfile.SYMTYPE
    info.mode = 0o777
    info.mtime = 0
    info.linkname = target
    out.addfile(info)


def parse_pkginfo(apk_path: Path) -> tuple[str, str]:
    with tarfile.open(apk_path, "r:gz") as apk:
        text = apk.extractfile(".PKGINFO").read().decode()
    fields = {}
    for line in text.splitlines():
        if " = " in line:
            key, value = line.split(" = ", 1)
            fields[key] = value
    return fields["pkgname"], fields["pkgver"]


def update_installed_db(db: str, versions: dict[str, str]) -> str:
    blocks = db.split("\n\n")
    for i, block in enumerate(blocks):
        package = next((line[2:] for line in block.splitlines() if line.startswith("P:")), None)
        if package in versions:
            blocks[i] = re.sub(r"(?m)^V:.*$", "V:" + versions[package], block)
    return "\n\n".join(blocks)


def read_layer_file(layer: Path, name: str) -> str:
    with tarfile.open(layer, "r") as archive:
        return archive.extractfile(name).read().decode()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-archive", type=Path, required=True)
    ap.add_argument("--jdk-archive", type=Path, required=True)
    ap.add_argument("--apk", type=Path, action="append", default=[])
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    with tempfile.TemporaryDirectory(prefix="corretto-repack-") as tmp_name:
        tmp = Path(tmp_name)
        base_dir = tmp / "base"
        jdk_dir = tmp / "jdk"
        base_dir.mkdir()
        jdk_dir.mkdir()
        with tarfile.open(args.base_archive) as src:
            src.extractall(base_dir)
        with tarfile.open(args.jdk_archive, "r:gz") as src:
            src.extractall(jdk_dir)

        manifest_path = base_dir / "manifest.json"
        manifest = json.loads(manifest_path.read_text())[0]
        config_path = base_dir / manifest["Config"]
        config = json.loads(config_path.read_text())
        old_layers = manifest["Layers"]
        if len(old_layers) != 4:
            raise SystemExit(f"expected the 4-layer secure image, found {len(old_layers)} layers")

        extracted_jdk = next(p for p in jdk_dir.iterdir() if p.is_dir())
        release = (extracted_jdk / "release").read_text()
        java_version = re.search(r'^JAVA_VERSION="([^"]+)"', release, re.M).group(1)
        runtime_version = re.search(r'^JAVA_RUNTIME_VERSION="([^"]+)"', release, re.M).group(1)
        corretto_version = re.search(r'^IMPLEMENTOR_VERSION="([^"]+)"', release, re.M).group(1)

        # Rebuild the second layer without the old JDK tree.
        old_jdk_layer = base_dir / old_layers[1]
        new_jdk_layer = tmp / "jdk-layer.tar"
        with tarfile.open(old_jdk_layer, "r") as src, tarfile.open(new_jdk_layer, "w") as out:
            for member in src:
                name = member.name.rstrip("/")
                if any(name == p.rstrip("/") or name.startswith(p) for p in EXCLUDED_PREFIXES):
                    continue
                if name.startswith("usr/bin/") and name.split("/")[-1] in EXCLUDED_BINARIES:
                    continue
                out.addfile(member, src.extractfile(member) if member.isfile() else None)
            add_fs_tree(out, extracted_jdk, JDK_PATH)
            add_symlink(out, "usr/lib/jvm/default-jvm", "java-17-amazon-corretto")
            for binary in EXCLUDED_BINARIES:
                add_symlink(out, f"usr/bin/{binary}", f"../lib/jvm/default-jvm/bin/{binary}")

        patch_layer = None
        apk_versions = {}
        if args.apk:
            patch_layer = tmp / "alpine-security-layer.tar"
            with tarfile.open(patch_layer, "w") as out:
                for apk_path in args.apk:
                    package, version = parse_pkginfo(apk_path)
                    apk_versions[package] = version
                    with tarfile.open(apk_path, "r:gz") as apk:
                        for member in apk:
                            name = member.name.lstrip("./")
                            if not name or name in APK_METADATA or name in {"PKGINFO", ".PKGINFO"} or name.startswith(".SIGN."):
                                continue
                            out.addfile(member, apk.extractfile(member) if member.isfile() else None)
                installed = read_layer_file(base_dir / old_layers[3], "lib/apk/db/installed")
                patched = update_installed_db(installed, apk_versions)
                info = tarfile.TarInfo("lib/apk/db/installed")
                data = patched.encode()
                info.size = len(data)
                info.mode = 0o644
                info.mtime = 0
                out.addfile(info, __import__("io").BytesIO(data))

        output_layers = [old_layers[0], "jdk-layer.tar", old_layers[2], old_layers[3]]
        if patch_layer:
            output_layers.append("alpine-security-layer.tar")
        output_manifest = dict(manifest)
        output_manifest["Layers"] = output_layers
        output_config = dict(config)
        output_config["created"] = "2026-11-18T00:00:00Z"
        labels = output_config.setdefault("config", {}).setdefault("Labels", {})
        labels["org.opencontainers.image.version"] = java_version
        labels["org.opencontainers.image.description"] = f"Amazon Corretto {corretto_version} on Alpine 3.24.1 with OpenSSL, X11 and Alpine security updates"
        output_config["rootfs"] = dict(output_config["rootfs"])
        layer_paths = [base_dir / old_layers[0], new_jdk_layer, base_dir / old_layers[2], base_dir / old_layers[3]]
        if patch_layer:
            layer_paths.append(patch_layer)
        output_config["rootfs"]["diff_ids"] = ["sha256:" + sha256(p) for p in layer_paths]
        output_config_path = tmp / "updated-config.json"
        output_config_path.write_text(json.dumps(output_config, separators=(",", ":")) + "\n")
        output_manifest_path = tmp / "manifest.json"
        output_manifest_path.write_text(json.dumps([output_manifest], separators=(",", ":")) + "\n")

        args.output.parent.mkdir(parents=True, exist_ok=True)
        with tarfile.open(args.output, "w") as out:
            for path, arcname in zip(layer_paths, output_layers):
                out.add(path, arcname=arcname, recursive=False)
            out.add(output_config_path, arcname="updated-config.json", recursive=False)
            out.add(output_manifest_path, arcname="manifest.json", recursive=False)
            out.add(base_dir / "repositories", arcname="repositories", recursive=False)

    print(f"jdk={java_version} runtime={runtime_version} corretto={corretto_version}")
    print(f"apk={apk_versions}")
    print(f"output={args.output}")
    print(f"sha256={sha256(args.output)}")


if __name__ == "__main__":
    main()
