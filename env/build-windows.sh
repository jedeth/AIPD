#!/bin/sh
# Construit l'installateur Windows (NSIS x64 + ia32, non signé) de PIA.
# Résultat : ../pia/electron/releases/pia Setup <version>.exe
set -e
cd "$(dirname "$0")"
PIA="$(cd ../pia && pwd)"

# 1. Build Angular de production (dans le conteneur de dev, qui doit tourner)
podman exec pia-dev yarn prod

# 2. Packaging Electron pour Windows dans un conteneur jetable avec Wine
podman run --rm --name pia-win-build \
  -v "$PIA":/project \
  -v pia-dev_pia_node_modules:/project/node_modules \
  -v pia-electron-cache:/root/.cache \
  -w /project \
  -e COREPACK_ENABLE_DOWNLOAD_PROMPT=0 -e CSC_IDENTITY_AUTO_DISCOVERY=false \
  docker.io/electronuserland/builder:wine \
  sh -c 'corepack enable && corepack prepare yarn@4.10.3 --activate >/dev/null \
         && node node_modules/electron-builder/cli.js --win --publish never'

ls -lh "$PIA"/electron/releases/*.exe
