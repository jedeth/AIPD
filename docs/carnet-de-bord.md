# Carnet de bord — PIA académie + assistant IA

> Dernière mise à jour : **2026-11-10** (création du carnet, reprise après un mois).
> Tenu à jour par la skill `aipd-reprise` à chaque pause et à chaque reprise.
> **Aucun secret ici** : ce fichier est versionné (dépôt `jedeth/AIPD`). Les secrets sont dans `env/server/.env` et `env/server/admin.secret` (droits 600).

## 1. Se reconnecter (30 s)

| Quoi | Valeur |
|---|---|
| Serveur de dev | `ia-raidf1.in.ac-paris.fr` (RHEL 9.6, Podman rootless, pas de GPU) |
| Accès | VS Code Remote-SSH depuis le poste Windows, dossier `~/AIPD` |
| Tunnels SSH à ouvrir | `-L 8080:127.0.0.1:8080` (application serveur) et `-L 4200:127.0.0.1:4200` (front de dev). VS Code les transfère souvent seul (onglet « Ports ») |
| Application (mode serveur) | http://localhost:8080 — après un déploiement, **Ctrl+Maj+R** (service worker) |
| Paramètres du front | Menu Paramètres → URL `http://localhost:8080/api`, Client ID / Client Secret : voir `env/server/admin.secret` |
| Compte admin | email `admin@pia.local`, mot de passe dans `env/server/admin.secret` |
| Front de dev (ng serve) | http://localhost:4200 — mode local par défaut, à basculer en mode serveur comme ci-dessus |
| PIA de démonstration | n° 8 « Cantine - badges élèves (essai prefill) » (contient des incohérences volontaires) |

## 2. État actuel (constaté le 2026-11-10)

- Conteneurs : `pia-front` (nginx, 8080), `pia-back` (Rails), `pia-db` (Postgres 16, base `pia_production`) et `pia-dev` (ng serve, 4200) sont tous **Up**. Le front répond 200, `/api/assistant/status` répond 401 sans jeton, ce qui est attendu.
- Branche déployée : **`feature/prefill`** sur les deux dépôts (front `dist` et image back).
  - pia : `815ca92d` (cohérence), `01e2f337` (réponses contingentées), `c8ae8fe1`, `adb4bc5c`
  - pia-back : `aaa4cd9` (cohérence), `566bf3c` (contingentées), `f9e09b3` (assistant)
- LLM : Albert API, modèle par défaut `gpt-oss-120b`, sélecteur de modèle actif (`ASSISTANT_MODEL_CHOICE=true`). Le quota (10 requêtes/min, 1 000/jour) est **partagé** entre tous les utilisateurs.
- 19 appels assistant tracés, le dernier le 2026-10-08. Aucune erreur 5xx sur les dernières 72 h.

## 3. Fonctions de l'assistant

| Fonction | Statut |
|---|---|
| Version simplifiée statique (36 questions) | Faite. Contenu en brouillon (`validated: false`), relecture DPO via `env/review/questions_vulgarisees_relecture.csv` |
| « M'aider » (reformulation par LLM) | Faite |
| Réponses contingentées (rappel, pré-remplissage, suggestions, applicabilité des droits) | Faite. Règles en brouillon dans `pia-back/config/assistant/dependencies.yml` (`rules_validated: false`) |
| Contrôles de cohérence (6 contrôles) | Faite. Contrôles en brouillon (`validated: false`) |
| Entretien guidé, relecture d'une réponse, glossaire | **À faire** (plan V1) |
| Suggestions de mesures en 3.1 | À faire (ce sont des entités distinctes) |

## 4. Prochaine étape

1. **Récupérer les décisions du DPO** de la réunion du 2026-10-13. Le document Claude Docs « Matrice de dépendances PIA » n'est plus accessible (supprimé ou plus partagé). Il peut être reconstruit depuis `dependencies.yml` si besoin.
2. Reporter ces décisions dans `dependencies.yml` (`validated`, `rules_validated`). Importer le CSV relu des questions simplifiées : `python3 env/tools/simplified_questions_review.py import`.
3. Décider de la suite :
   - fusionner `feature/prefill` dans `feature/assistant` ;
   - attaquer les fonctions V1 restantes ;
   - corriger la faille amont `PiaPolicy#show?` (`is_example`), sur une branche séparée.

## 5. Commandes utiles

```bash
# État
podman ps --format '{{.Names}} {{.Status}}' | grep pia
# Rebuild + redéploiement du front serveur
podman exec pia-dev yarn prod && podman restart pia-front
# Rebuild + redéploiement du back (2 rm séparés : --force-recreate n'est pas fiable)
cd ~/AIPD/env/server && podman-compose build back && podman rm -f pia-front; podman rm -f pia-back; podman-compose up -d
# Tests back (base jetable)
~/AIPD/env/server/test-back.sh
# Installateur Windows Electron
~/AIPD/env/build-windows.sh
# Logs back
podman logs --since 1h pia-back
```

Les détails d'exploitation (sauvegardes, mails, passage en production) sont dans `env/server/README.md`.

## 6. Règles du projet (à ne pas oublier)

- Les réponses réelles des utilisateurs ne partent **que vers Albert API**. Claude sert uniquement au développement et au contenu statique (textes publics du questionnaire).
- Les modifications restent isolées sur les branches `feature/*`, pour pouvoir rebaser sur l'amont LINCnil.
- On ne touche pas aux autres conteneurs du serveur (`chatbot-*`, etc.).
- On ne commite que sur demande, et jamais un secret.
- L'IA propose, l'utilisateur décide. Les règles métier attendent le visa du DPO.

## 7. Journal

- **2026-10-08 → 10-09** : conteneurisation (dev, serveur, Electron Windows) ; assistant Albert (M'aider, sélecteur de modèle) ; questions simplifiées statiques ; matrice de dépendances pour le DPO ; réponses contingentées et cohérence sur `feature/prefill`.
- **2026-11-10** : reprise après un mois. Tous les services tournent. Création de ce carnet et de la skill `aipd-reprise`.
