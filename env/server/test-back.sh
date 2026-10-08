#!/bin/sh
# Lance la suite de tests de pia-back dans des conteneurs jetables
# (Postgres temporaire, gems de dev/test dans un volume de cache). N'affecte pas la stack pia-server.
set -e
cd "$(dirname "$0")"
BACK="$(cd ../../pia-back && pwd)"
NET=pia-test-net
podman network exists $NET || podman network create $NET >/dev/null
podman rm -f pia-test-db >/dev/null 2>&1 || true
podman run -d --rm --name pia-test-db --network $NET -e POSTGRES_PASSWORD=test docker.io/library/postgres:16-alpine >/dev/null
trap 'podman rm -f pia-test-db >/dev/null 2>&1' EXIT
until podman exec pia-test-db pg_isready -U postgres >/dev/null 2>&1; do sleep 1; done

podman run --rm --network $NET -v "$BACK":/rails -v pia-test-bundle:/usr/local/bundle -w /rails \
  -e RAILS_ENV=test -e DATABASE_URL=postgres://postgres:test@pia-test-db:5432/pia_test \
  -e PARALLEL_WORKERS="${PARALLEL_WORKERS:-4}" -e BUNDLE_DEPLOYMENT=0 -e BUNDLE_WITHOUT= \
  localhost/pia-back:latest \
  sh -c 'bundle install --quiet && bin/rails db:prepare >/dev/null && bin/rails test "$@"' -- "$@"
