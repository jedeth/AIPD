#!/usr/bin/env bash
# Première installation de MonServiceSécurisé en local : base, migrations, sel de hachage.
# Idempotent : ne réinsère pas le sel s'il est déjà en base.
set -euo pipefail
cd "$(dirname "$0")"

[ -f .env ] || { echo "env/mss/.env manquant" >&2; exit 1; }
set -a; . ./.env; set +a

podman-compose build mss-web
podman-compose up -d mss-db
until podman exec mss-db pg_isready -U mss -d mss >/dev/null 2>&1; do sleep 2; done

URL_BDD="postgres://mss:${MSS_DB_PASSWORD}@mss-db:5432/mss"
podman run --rm --network mss_default --env-file .env \
  -e NODE_ENV=development -e URL_SERVEUR_BASE_DONNEES="$URL_BDD" \
  localhost/mss-web:latest pnpm run migration-bdd

if [ "$(podman exec mss-db psql -U mss -d mss -tAc 'select count(*) from sels_de_hachage')" = "0" ]; then
  HASH=$(podman run --rm localhost/mss-web:latest \
    node --import tsx scripts/dev-init-sel.js "$CHIFFREMENT_SEL_DE_HASHAGE_1")
  podman exec mss-db psql -U mss -d mss -c \
    "insert into sels_de_hachage (version, empreinte) values (1, '$HASH');"
fi

podman-compose up -d mss-web
echo "MonServiceSécurisé : http://localhost:8090 (via tunnel SSH -L 8090:127.0.0.1:8090)"
