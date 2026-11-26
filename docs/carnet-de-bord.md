# Carnet de bord — PIA académie + assistant IA

> Dernière mise à jour : **2026-11-26** (avant la séance DPO).
> Tenu à jour par la skill `aipd-reprise` à chaque pause et à chaque reprise.
> **Aucun secret ici** : ce fichier est versionné (dépôt `jedeth/AIPD`). Les secrets sont dans `env/server/.env` et `env/server/admin.secret` (droits 600).

## 1. Se reconnecter (30 s)

| Quoi | Valeur |
|---|---|
| Serveur de dev | `ia-raidf1.in.ac-paris.fr` (RHEL 9.6, Podman rootless, pas de GPU) |
| Accès | VS Code Remote-SSH depuis le poste Windows, dossier `~/AIPD` |
| Tunnels SSH à ouvrir | `-L 8080:127.0.0.1:8080` (application serveur) et `-L 4200:127.0.0.1:4200` (front de dev). VS Code les transfère souvent seul (onglet « Ports ») |
| Si le transfert VS Code se fige (page qui tourne dans le vide) | Arrêter le transfert de 8080/8090 dans VS Code (ou tuer l'ancien `ssh.exe` : `netstat -ano \| findstr ":8080 :8090"`), puis dans PowerShell : `ssh -N -L 8080:127.0.0.1:8080 -L 8090:127.0.0.1:8090 iarag@ia-raidf1.in.ac-paris.fr` (n'affiche rien, à laisser ouvert). Garder 8080 côté Windows |
| Application (mode serveur) | http://localhost:8080 — après un déploiement, **Ctrl+Maj+R** (service worker) |
| Paramètres du front | Menu Paramètres → URL `http://localhost:8080/api`, Client ID / Client Secret : voir `env/server/admin.secret` |
| Compte admin | email `admin@pia.local`, mot de passe dans `env/server/admin.secret` |
| MonServiceSécurisé (local) | http://localhost:8090 (tunnel `-L 8090:127.0.0.1:8090`), « Se connecter » → formulaire local (e-mail, sans mot de passe). Compte `admin@pia.local` créé le 2026-11-17 (rectorat de Paris, téléphone fictif). Doc : `env/mss/README.md` |
| Front de dev (ng serve) | http://localhost:4200 — mode local par défaut, à basculer en mode serveur comme ci-dessus |
| PIA de démonstration | n° 8 « Cantine - badges élèves (essai prefill) » (contient des incohérences volontaires) |

## 2. État actuel (constaté le 2026-11-26)

- Conteneurs `pia-front` (8080), `pia-back`, `pia-db`, `pia-dev` (4200), `mss-web` (127.0.0.1:8090) et `mss-db` : tous **Up**. Le front répond 200, `/api/assistant/status` 401 sans jeton (attendu). Aucune erreur 5xx sur 72 h. 33 appels assistant tracés (dernier le 2026-11-17).
- Branche déployée : **`feature/guided`** sur `pia` (`1e8af230`) et `pia-back` (`617af92`) : parcours guidé complet, étapes 1 à 5. Commits **locaux uniquement** : `origin` = LINCnil, on n'y pousse pas (dépôts privés `jedeth/pia` et `jedeth/pia-back` à créer).
- MonServiceSécurisé : branche `local/connexion-dev` (`a881e9562`, passerelle `/integration/pia`, secret partagé dans les deux `.env`). `pia-back` est relié au réseau `mss_default`. 1 compte (`admin@pia.local`) et 1 service (créé depuis la PIA n° 10). Ne jamais exposer au-delà de 127.0.0.1.
- PIA n° 10 « test_parcours_assiste » : parcours de test complet ; brouillons nettoyés (un seul par question) après l'analyse du premier export PDF.
- LLM : Albert API, `gpt-oss-120b` par défaut ; la déduction du parcours fait deux appels en parallèle et une recherche dans les collections Légifrance et décisions CNIL d'Albert. Le 2026-11-20, Albert débitait 13 tokens/s (contre ~55 le 17/11) : délais portés à 240 s (`LLM_TIMEOUT`) et 300 s (nginx, `env/server/nginx.conf.template`, commité dans `57600d2`). Une analyse peut prendre 2-3 min : la lancer avant la démo.
- Démo DPO : déroulé dans Claude Docs (https://claude.ai/artifact/2jTNMqMf4sdAj2ReXtqpJ6). PIA n° 10 = parcours complet avec service MSS ; PIA n° 11 « Démo infirmerie » : parcours vierge, à lancer en direct (essai du 2026-11-26 : 26 propositions en 54 s, Albert à 34 tokens/s ; profil d'essai supprimé ensuite).
- Code : rien de non commité dans `pia`, `pia-back`, `mon-service-securise`. Dans `~/AIPD`, les pointeurs `pia` et `pia-back` ne sont pas mis à jour, volontairement.
- Incubateur : demande Grist n° 24 (assistant PIA) scorée 65/100, fiche `SUIVI.md` poussée dans le Grist ; le même jour, scoring et suivi des demandes n° 11 (assistant de langues, portefeuille) et n° 25 (Établi, dépôt Établi).

## 3. Fonctions de l'assistant

| Fonction | Statut |
|---|---|
| Version simplifiée statique (36 questions) | Faite. Contenu en brouillon (`validated: false`), relecture DPO via `env/review/questions_vulgarisees_relecture.csv` |
| « M'aider » (reformulation par LLM) | Faite |
| Réponses contingentées (rappel, pré-remplissage, suggestions, applicabilité des droits) | Faite. Règles en brouillon dans `pia-back/config/assistant/dependencies.yml` (`rules_validated: false`) |
| Contrôles de cohérence (6 contrôles) | Faite. Contrôles en brouillon (`validated: false`) |
| Entretien guidé, relecture d'une réponse, glossaire | **À faire** (plan V1) |
| Suggestions de mesures en 3.1 | À faire (ce sont des entités distinctes) |
| Parcours guidé (`/#/pia/:id/parcours`) : décrire → vérifier (IA + recherche Légifrance/CNIL) → compléter → pré-remplir le PIA (sections 1-2) | Fait (prototype, 26 informations). Champs en brouillon dans `pia-back/config/assistant/guided.yml` (`validated: false`) |
| Étape 4 Sécurité : service créé dans MonServiceSécurisé, risques/mesures relus, menaces reportées en 3.2.2/3.3.2/3.4.2 | Fait (prototype). Correspondances en brouillon dans `pia-back/config/assistant/security.yml` (DPO + RSSI). Étape 5 Valider faite : bilan, mesures indispensables MSS en 3.1 (une fiche par catégorie), pré-remplissage rejouable |

## 4. Prochaine étape

1. **Séance DPO 2026-11-26** (suivre le déroulé ci-dessus) : démo du parcours guidé sur la PIA n° 10 (étapes 1 à 5) ; faire viser `pia-back/config/assistant/guided.yml` (26 informations), `security.yml` (correspondances PIA → MSS, avec le RSSI) et la répartition des informations entre questions CNIL (reprise complète ou renvoi). Points à lui signaler : intérêt légitime exclu pour une autorité publique ; durées de conservation et cadre réglementaire ; inscription MSS bloquée dans le navigateur (« Vos consentements »).
1 bis. **Demandes de la séance DPO du 2026-11-26** (à traiter) :
   - Volume : Albert doit proposer une estimation chiffrée du nombre de personnes (ordre de grandeur d'un lycée), pas seulement une tranche en liste déroulante.
   - Données : pour chaque catégorie de données, préciser le détail (nom, prénom, classe…).
   - Mesures MSS → PIA : report automatique en 3.1 au pré-remplissage (déployé le 2026-11-26, non commité) ; surtout, **qualifier les mesures MSS pour qu'elles coïncident avec les mesures proposées par le PIA** (table de correspondance mesure MSS → mesure PIA, à faire viser par le DPO et le RSSI).
   - Chaque mesure proposée par MSS doit être indiquée **mise en œuvre ou non** par le porteur de projet.
   - Décisions du 2026-11-26 sur ces deux points : (a) les mesures du PIA sont des **catégories** ; chaque mesure précise de MSS doit être rangée dans une catégorie PIA (aucune mesure « hors catégorie ») ; (b) le porteur indique l'état (mise en œuvre ou non) **dans le parcours du PIA, après l'import**, et non dans MSS.
   - Premier jet de la table de correspondance (135 mesures MSS → 29 catégories PIA, 30 rattachements à confirmer) : `pia-back/config/assistant/measures.yml` (brouillon, pas encore utilisé par le code), tableur et PDF dans `env/review/`, page de relecture en ligne pour le DPD avec 7 questions (https://claude.ai/artifact/DFGUf8GnCcTSvazetZoa1r, source `env/review/mesures-mss-pia.html`, à partager en « Contributeur »). Suite : reporter ses réponses, puis brancher l'import sur ce fichier et ajouter la saisie « mise en œuvre ou non » à l'étape 5.
   - Ouverture de MSS local sans authentification depuis le parcours (codé le 2026-11-26 : `/oidc/connexion-directe`, option `MSS_DIRECT_LOGIN`, déployé le 2026-11-26, non commité ; à essayer dans le navigateur).
2. Reporter ses décisions dans `guided.yml`, `security.yml` et `dependencies.yml` (`validated: true`).
3. Créer les dépôts privés `jedeth/pia`, `jedeth/pia-back` (et `mon-service-securise`) pour sauvegarder le code hors du serveur.
4. Ensuite : mise en production (serveur DRASI, authentification), schéma de décision de la base légale à mettre à jour (D12), table de correspondance des catégories PIA ↔ MSS demandée par le DPO.

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
- **2026-11-10** : reprise après un mois. Tous les services tournent. Création de ce carnet et de la skill `aipd-reprise`. Matrice de dépendances reconstruite depuis `dependencies.yml`.
- **2026-11-10 (pause)** : matrice de dépendances reconstruite ; document « Questions élémentaires PIA — sections 1 et 2 » rédigé pour le DPO (29 questions, arbre de décision de la base légale). Aucun code modifié. Reprise : relecture DPO des deux documents.
- **2026-11-10** : clone de MonServiceSécurisé (Apache-2.0, Node/Express + Svelte + Postgres 14) pour le futur projet combiné PIA + analyse de risques.
- **2026-11-10** : installation locale de MonServiceSécurisé (Podman, Postgres 14, chiffrement ChaCha20 actif, e-mails dans les logs) ; connexion ProConnect contournée par un formulaire local (choix utilisateur).
- **2026-11-10 (pause)** : MonServiceSécurisé installé et vérifié dans le navigateur ; note de cadrage du combo PIA + MSS rédigée pour le DPO. Reprise : retours du DPO sur les 3 documents (matrice, questions élémentaires, note de cadrage).
- **2026-11-17** : reprise, état constaté : les 6 conteneurs (`pia-*`, `mss-*`) sont Up, 8080/4200/8090 répondent 200, aucune erreur 5xx, rien de non commité. En attente des retours du DPO.
- **2026-11-17** : retours du DPO reportés dans « Questions élémentaires » (18 validées, 10 à reformuler, A4 refusée, D12 ajoutée). Note de cadrage : option 2 validée par le DPO, ajout de la variante « portail unique » (pas de fusion du code) avec maquette des 5 écrans.
- **2026-11-17** : parcours guidé (branche `feature/guided`, commits locaux `42cc647` / `ae41bd8e`) : déduction par Albert, recherche de textes dans les collections Légifrance et décisions CNIL d'Albert, étape 3, report en brouillon dans les questions 1.1.1 à 2.2.6 sans écraser l'existant. Testé par l'utilisateur sur la PIA n° 10. « M'aider » n'invente plus de durées.
- **2026-11-17** : parcours guidé étendu aux sections 1 et 2 complètes (26 informations en blocs A-D, report sur les 18 questions 1.1.1-2.2.7, droits selon la base légale), deux appels Albert en parallèle (~45 s), polices agrandies. Séance DPO prévue vendredi 2026-11-20. pia/pia-back : commits locaux, pas de remote personnel (à créer : jedeth/pia, jedeth/pia-back).
- **2026-11-17** : étape 4 Sécurité : passerelle `/integration/pia` dans MSS (commit local `a881e9562`), pia-back relié au réseau `mss_default`, service créé dans MSS depuis la PIA n° 10 (niveau avancé, 8 risques dont 7 élevés, 113 mesures), menaces reportées en section 3. Commits locaux pia-back `4c063bb`, pia `ce5e962f`.
- **2026-11-17** : étape 5 Valider, parcours linéaire, report rejouable sans doublon (après analyse du premier export PDF) ; demande Grist n° 24 scorée (65/100) et fiche `SUIVI.md` poussée dans le Grist de l'incubateur.
- **2026-11-17 (pause)** : parcours guidé complet (étapes 1 à 5, MonServiceSécurisé relié), premier export analysé et corrigé ; demandes 24, 11 et 25 scorées et suivies dans le Grist de l'incubateur ; widget de scoring rendu générique. Reprise : séance DPO du 2026-11-20.
- **2026-11-20** : reprise, état constaté : les 6 conteneurs sont Up, 8080/4200 répondent 200 (MSS 302 vers la connexion), aucune erreur 5xx depuis le 2026-11-17, rien de non commité. Jour de la séance DPO.
- **2026-11-20** : déroulé de démo DPO rédigé ; analyse coupée par la lenteur d'Albert (90 s), délais portés à 240/300 s, conteneurs `pia-back` et `pia-front` recréés.
- **2026-11-26** : carnet et mémoire mis à jour avant la séance DPO (changement de compte Claude Code).
- **2026-11-26** : reprise, état constaté : les 6 conteneurs sont Up, 8080/4200/8090 répondent 200, aucune erreur 5xx sur 24 h, 33 appels assistant (dernier le 2026-11-17), rien de non commité dans `pia`, `pia-back`, `mon-service-securise`.
- **2026-11-26** : déroulé de démo recréé sur le nouveau compte Claude (l'ancien lien était inaccessible) ; PIA n° 11 remise à zéro pour la démo ; tunnel 8080/8090 figé côté Windows (ancien `ssh.exe`), rétabli par un `ssh -N -L` depuis PowerShell.
