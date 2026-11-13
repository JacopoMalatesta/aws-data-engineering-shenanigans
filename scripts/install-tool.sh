#!/usr/bin/env bash
# Download a pinned release artifact, verify its sha256 and install it as
# /usr/local/bin/<tool>. Shared by every vendored-tool install step in the
# CI workflows; call sites pass the version-pinned URL and checksum from
# constants.py.
#
# Usage:
#   install-tool.sh --url <download-url> --sha256 <expected-sha256> \
#     --tool <name> --kind <raw|tar|gzip>
#     kind: raw (plain binary) | tar (gzip tarball) | gzip (single file)
set -euo pipefail

url=""
sha256=""
tool=""
kind=""
while [[ $# -gt 0 ]]; do
  case "${1}" in
  --url) url="${2:?--url needs a value}" ;;
  --sha256) sha256="${2:?--sha256 needs a value}" ;;
  --tool) tool="${2:?--tool needs a value}" ;;
  --kind) kind="${2:?--kind needs a value}" ;;
  *)
    echo "unknown argument '${1}' (every argument must be a --flag value pair)" >&2
    exit 2
    ;;
  esac
  shift 2
done

if [[ -z "${url}" || -z "${sha256}" || -z "${tool}" || -z "${kind}" ]]; then
  echo "all of --url, --sha256, --tool and --kind are required" >&2
  exit 2
fi

case "${kind}" in
raw) suffix="" ;;
gzip) suffix=".gz" ;;
tar) suffix=".tar.gz" ;;
*)
  echo "unknown --kind '${kind}' (expected raw, tar or gzip)" >&2
  exit 2
  ;;
esac

workdir="$(mktemp -d)"
trap 'rm -rf "${workdir}"' EXIT
download="${workdir}/${tool}${suffix}"

curl -fsSL -o "${download}" "${url}"
printf '%s  %s\n' "${sha256}" "${download}" | sha256sum --check --strict -

if [[ "${kind}" == "raw" ]]; then
  binary="${download}"
elif [[ "${kind}" == "gzip" ]]; then
  gunzip "${download}"
  binary="${workdir}/${tool}"
else
  # Tarballs nest the binary at varying depths (e.g. version-prefixed
  # directories); pick the first regular file matching the tool name.
  tar -xzf "${download}" -C "${workdir}"
  binary="$(find "${workdir}" -type f -name "${tool}" -print -quit)"
fi

if [[ ! -f "${binary}" ]]; then
  echo "no '${tool}' binary found after extracting ${download}" >&2
  exit 1
fi
sudo install -m 0755 "${binary}" "/usr/local/bin/${tool}"
