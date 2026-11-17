#!/usr/bin/env python3
"""Replace the Corretto JDK layer in a Docker save archive.

The input archive is the existing X11-secure image. All layers except the
JDK-containing layer are retained byte-for-byte, so the Alpine/OpenSSL/X11
security updates are not downgraded.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import stat
import tarfile
import tempfile
from pathlib import Path

JDK_DIR = "usr/lib/jvm/java-17-amazon-corretto"
JDK_VERSION = "17.0.21"
JDK_RELEASE = "17.0.21.0.11"
EXCLUDED_PREFIXES = ("usr/lib/jvm/",)
EXCLUDED_BINARIES = {
    "java", "javac", "jar", "jarsigner", "javadoc", "javap", "jcmd", "jconsole",
    "jdb", "jdeprscan", "jdeps", "jfr", "jhsdb", "jimage", "jinfo", "jlink",
    "jmap", "jmod", "jpackage", "jps", "jrunscript", "jshell", "jstack", "jstat",
    "jstatd", "keytool", "rmiregistry", "serialver",
}


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


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-archive", type=Path, required=True)
    ap.add_argument("--jdk-archive", type=Path, required=True)
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
        layers = manifest["Layers"]
        if len(layers) != 4:
            raise SystemExit(f"expected the 4-layer secure image, found {len(layers)} layers")

        # The second layer contains the original Corretto 17.0.19 JDK plus
        # Alpine runtime packages. Rebuild it without the old JDK tree.
        old_jdk_layer = base_dir / layers[1]
        new_jdk_layer = tmp / "jdk-layer.tar"
        with tarfile.open(old_jdk_layer, "r") as src, tarfile.open(new_jdk_layer, "w") as out:
            for member in src:
                name = member.name.rstrip("/")
                if any(name == p.rstrip("/") or name.startswith(p) for p in EXCLUDED_PREFIXES):
                    continue
                if name.startswith("usr/bin/") and name.split("/")[-1] in EXCLUDED_BINARIES:
                    continue
                out.addfile(member, src.extractfile(member) if member.isfile() else None)

            extracted = next(p for p in jdk_dir.iterdir() if p.is_dir())
            add_fs_tree(out, extracted, JDK_DIR)
            add_symlink(out, "usr/lib/jvm/default-jvm", "java-17-amazon-corretto")
            for binary in EXCLUDED_BINARIES:
                add_symlink(out, f"usr/bin/{binary}", f"../lib/jvm/default-jvm/bin/{binary}")

        # Keep original layer 0, OpenSSL layer 2 and X11 layer 3 byte-for-byte.
        output_manifest = dict(manifest)
        output_manifest["RepoTags"] = ["amazoncorretto:17-alpine"]
        output_manifest["Layers"] = [layers[0], "jdk-17.0.21-layer.tar", layers[2], layers[3]]
        output_config = dict(config)
        output_config["created"] = "2026-11-17T00:00:00Z"
        output_config.setdefault("config", {}).setdefault("Labels", {})["org.opencontainers.image.version"] = JDK_VERSION
        output_config["config"]["Labels"]["org.opencontainers.image.description"] = "Amazon Corretto 17.0.21 on Alpine 3.24.1 with OpenSSL and X11 security updates"
        output_config["rootfs"] = dict(output_config["rootfs"])
        output_config["rootfs"]["diff_ids"] = [
            "sha256:" + sha256(base_dir / layers[0]),
            "sha256:" + sha256(new_jdk_layer),
            "sha256:" + sha256(base_dir / layers[2]),
            "sha256:" + sha256(base_dir / layers[3]),
        ]
        output_config_path = tmp / "updated-config.json"
        output_config_path.write_text(json.dumps(output_config, separators=(",", ":")) + "\n")
        output_manifest_path = tmp / "manifest.json"
        output_manifest_path.write_text(json.dumps([output_manifest], separators=(",", ":")) + "\n")

        args.output.parent.mkdir(parents=True, exist_ok=True)
        with tarfile.open(args.output, "w") as out:
            out.add(base_dir / layers[0], arcname=layers[0], recursive=False)
            out.add(new_jdk_layer, arcname="jdk-17.0.21-layer.tar", recursive=False)
            out.add(base_dir / layers[2], arcname=layers[2], recursive=False)
            out.add(base_dir / layers[3], arcname=layers[3], recursive=False)
            out.add(output_config_path, arcname="updated-config.json", recursive=False)
            out.add(output_manifest_path, arcname="manifest.json", recursive=False)
            out.add(base_dir / "repositories", arcname="repositories", recursive=False)

    print(f"output={args.output}")
    print(f"sha256={sha256(args.output)}")


if __name__ == "__main__":
    main()
