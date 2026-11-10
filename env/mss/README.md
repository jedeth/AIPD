# MonServiceSécurisé (ANSSI) — instance locale

Instance de développement isolée, en vue du combo PIA + MonServiceSécurisé.

- Sources : `~/AIPD/mon-service-securise`, branche **`local/connexion-dev`** (master ANSSI + connexion locale).
- Conteneurs : `mss-web` (Node 24, port `127.0.0.1:8090`) et `mss-db` (Postgres 14, non publié), projet podman-compose `mss`.
- Accès : tunnel SSH `-L 8090:127.0.0.1:8090`, puis http://localhost:8090 → « Se connecter ».

## Connexion sans ProConnect

MSS n'accepte que ProConnect. La branche `local/connexion-dev` ajoute `src/adaptateurs/adaptateurOidcLocal.ts` :
avec `MSS_CONNEXION_LOCALE=true` (et `NODE_ENV` ≠ `production`), « Se connecter » ouvre un formulaire
e-mail / prénom / nom, **sans aucune vérification d'identité**. L'instance ne doit donc jamais être exposée
au-delà de `127.0.0.1`. Un nouvel e-mail mène à la création de compte (choix de l'organisation via
l'API publique recherche-entreprises).

## Configuration

`.env` (droits 600, jamais versionné) : mot de passe Postgres, secrets cookie/JWT, clé ChaCha20
(chiffrement au repos actif), sel de hachage, limites de débit. Les e-mails ne partent pas : ils sont écrits
dans les logs (`podman logs mss-web`). Pas de Brevo, Sentry, Matomo, Crisp ni MonProfilAnssi.

## Commandes

```bash
./init.sh                                        # première installation (build, migrations, sel)
podman-compose up -d                             # démarrage
podman logs -f mss-web                           # logs
# mise à jour depuis l'ANSSI
git -C ~/AIPD/mon-service-securise fetch origin && git -C ~/AIPD/mon-service-securise rebase origin/master
podman-compose build mss-web && podman rm -f mss-web; podman-compose up -d
```

Le sel `CHIFFREMENT_SEL_DE_HASHAGE_1` est lié à son empreinte en base : ne pas le changer sans réinitialiser la base.
