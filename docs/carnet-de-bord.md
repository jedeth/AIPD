# Carnet de bord — PIA académie + assistant IA

> Dernière mise à jour : **2026-11-17** (reprise).
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
| MonServiceSécurisé (local) | http://localhost:8090 (tunnel `-L 8090:127.0.0.1:8090`), « Se connecter » → formulaire local (e-mail, sans mot de passe). Compte `admin@pia.local` créé le 2026-11-17 (rectorat de Paris, téléphone fictif). Doc : `env/mss/README.md` |
| Front de dev (ng serve) | http://localhost:4200 — mode local par défaut, à basculer en mode serveur comme ci-dessus |
| PIA de démonstration | n° 8 « Cantine - badges élèves (essai prefill) » (contient des incohérences volontaires) |

## 2. État actuel (constaté le 2026-11-17, à la reprise)

- Conteneurs : `pia-front` (nginx, 8080), `pia-back` (Rails), `pia-db` (Postgres 16, base `pia_production`) et `pia-dev` (ng serve, 4200) sont tous **Up**. Le front répond 200, `/api/assistant/status` répond 401 sans jeton, ce qui est attendu.
- Branche déployée : **`feature/guided`** (issue de `feature/prefill`) sur les deux dépôts (front `dist` et image back). Commits **locaux uniquement** : `origin` pointe vers LINCnil (amont CNIL), on n'y pousse pas.
  - pia : `ae41bd8e`, puis commit « grouped by block » (parcours guidé)
  - pia-back : `42cc647`, puis commit « covers sections 1 and 2 » (parcours guidé, report dans le PIA)
  - pia : `815ca92d` (cohérence), `01e2f337` (réponses contingentées), `c8ae8fe1`, `adb4bc5c`
  - pia-back : `aaa4cd9` (cohérence), `566bf3c` (contingentées), `f9e09b3` (assistant)
- LLM : Albert API, modèle par défaut `gpt-oss-120b`, sélecteur de modèle actif (`ASSISTANT_MODEL_CHOICE=true`). Le quota (10 requêtes/min, 1 000/jour) est **partagé** entre tous les utilisateurs.
- 19 appels assistant tracés, le dernier le 2026-10-08. Aucune erreur 5xx sur les dernières 24 h.
- MonServiceSécurisé (ANSSI) : installé le 2026-11-10, conteneurs `mss-web` (127.0.0.1:8090) et `mss-db`, projet `mss` (`env/mss/`). Sources `~/AIPD/mon-service-securise` (ignoré par git), branche `local/connexion-dev` = master ANSSI + connexion locale sans ProConnect (correctif commité localement : `8cfc3c8ab`, pas de dépôt distant). Ne jamais exposer au-delà de 127.0.0.1.
- MSS au 2026-11-17 : conteneurs Up, page d'accueil 200, aucun compte ni service encore créé, aucune erreur.
- Code : rien de non commité dans `pia`, `pia-back` ni `mon-service-securise`. Dans `~/AIPD`, les pointeurs `pia` et `pia-back` (sous-dépôts) ne sont pas mis à jour vers `feature/prefill`, volontairement pour l'instant.

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

0. **Séance DPO vendredi 2026-11-20** : démo du parcours guidé sur la PIA n° 10 (étapes 1 à 4), faire viser `guided.yml` (26 informations) et `security.yml` (correspondances PIA → MSS, avec le RSSI). Signaler : l'inscription MSS par le navigateur bloque sur « Vos consentements » (cause non trouvée, compte créé par l'API) ; durées de conservation et cadre réglementaire restent à valider.

1. **Récupérer les décisions du DPO** de la réunion du 2026-10-13. La « Matrice de dépendances PIA » a été reconstruite le 2026-11-10 (Claude Docs, https://claude.ai/artifact/WpZsq1ePB3ioEFDLhi4PDh) : décisions DPO à ressaisir dedans.
2. Reporter ces décisions dans `dependencies.yml` (`validated`, `rules_validated`). Importer le CSV relu des questions simplifiées : `python3 env/tools/simplified_questions_review.py import`.
3. Faire relire au DPO « Questions élémentaires PIA — sections 1 et 2 » (https://claude.ai/artifact/CX67rPkbtZPYK4aS78kHX2) : 29 questions qui alimentent les 18 questions CNIL des sections 1-2 (futur « parcours guidé »). La section 3 sera traitée plus tard avec MonServiceSécurisé (ANSSI).
4. Faire valider au DPO la note de cadrage « Combo PIA + MonServiceSécurisé » (https://claude.ai/artifact/UgPdhSWYGDkz2eVtSDr8Dy) : option 2 recommandée (socle commun + passerelles : import Excel vers MSS, API publique MSS en lecture pour mesures/risques).
5. Décider de la suite :
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
