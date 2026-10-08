# PIA en mode client/serveur (pia + pia-back)

Projet Podman `pia-server` : nginx (front + proxy) -> pia-back (Rails/Puma) -> PostgreSQL 16.

| Conteneur  | Rôle                                                        |
|------------|-------------------------------------------------------------|
| pia-front  | nginx : sert `pia/dist/pia-angular/browser`, proxy `/api/` et `/rails/` |
| pia-back   | API Rails (image construite depuis `../../pia-back`)        |
| pia-db     | PostgreSQL 16 (volume `pia-server_pia_pgdata`)              |

Accès : http://localhost:8080 (lié à 127.0.0.1 → tunnel SSH `-L 8080:localhost:8080`).

## Fichiers
- `.env` : secrets et réglages (600, non versionné)
- `admin.secret` : CLIENT_ID / CLIENT_SECRET OAuth + compte admin initial (600, non versionné)
- `zz_container_overrides.rb` : monté dans `config/initializers/` de pia-back
  (SSL désactivable, port dans DEFAULT_HOST, mails vers fichiers si pas de SMTP)
- `nginx.conf.template`, `Containerfile.back`, `compose.yaml`

## Réglages dans le front (Paramètres > Serveur, une fois par navigateur)
- URL du serveur : `http://localhost:8080/api`
- Client ID / Client Secret : voir `admin.secret`

## Opérations courantes (depuis ce dossier)
    podman-compose up -d                  # démarrer
    podman-compose down                   # arrêter (les volumes sont conservés)
    podman logs -f pia-back               # logs API

    # Mettre à jour le front : rebuild Angular (conteneur de dev pia-dev)
    podman exec pia-dev yarn prod

    # Mettre à jour pia-back : git pull dans ../../pia-back puis
    podman-compose build back
    # recréer réellement les conteneurs (--force-recreate n'est pas fiable avec podman-compose ;
    # pia-front dépend de pia-back, on les supprime ensemble — les volumes sont conservés)
    podman rm -f pia-front; podman rm -f pia-back; podman-compose up -d   # migrations auto (db:prepare)

    # Après modification de .env : même commande de recréation (sans build)

    # Tests pia-back (conteneurs jetables, base de test temporaire)
    ./test-back.sh

    # Codes d'activation des comptes (tant que SMTP_ADDRESS est vide)
    podman exec pia-back sh -c 'ls tmp/mails; cat tmp/mails/<email>'

    # Sauvegarde base + pièces jointes
    podman exec pia-db pg_dump -U pia pia_production | gzip > pia-$(date +%F).sql.gz
    podman run --rm -v pia-server_pia_storage:/s:ro -v "$PWD":/b docker.io/library/alpine tar czf /b/storage-$(date +%F).tgz -C /s .

## Passage en accès réseau réel (plus tard)
1. Exposer nginx sur l'interface voulue + HTTPS (certificat), `PIA_FORCE_SSL=true`
2. `DEFAULT_HOST=<nom DNS>` dans `.env`, `ALLOWED_CORS_ORIGINS=https://<nom DNS>`
3. Renseigner `SMTP_ADDRESS`, `SMTP_PORT`, `EMAIL_FROM` pour l'envoi réel des mails
