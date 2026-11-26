---
projet: Assistant IA pour les analyses d'impact (PIA)
depot: AIPD
grist_demande: 24
porteur: Jérôme de Thésut
commanditaire: Bartholomé Gillery (DPO de l'académie de Paris)
phase: Prototype
meteo: vert
score: 65
axe_metier: 16
axe_souverainete: 12
axe_faisabilite: 14
axe_economie: 10
date_debut: 2026-11-17
date_fin_prevue: 2027-02-01
derniere_action: 2026-11-26
prochaine_action: Relecture par le DPO de la table de correspondance des mesures et réponses aux sept questions ; puis intégration au parcours
responsable: Bartholomé Gillery
echeance:
blocage: 
decision_attendue: Validation par le DPO et le RSSI de la table de correspondance des mesures ; visa des listes du parcours ; forme du déploiement (académie ou mutualisé)
charge_estimee: 
charge_consommee: 2
---

## Objectif

Aider les agents non spécialistes à réaliser une analyse d'impact (AIPD) avec le logiciel PIA de la CNIL : description libre du projet, propositions d'Albert à valider, pré-remplissage des sections 1 et 2, risques de sécurité calculés par MonServiceSécurisé (ANSSI) pour la section 3. Public : porteurs de projets de l'académie, DPO et RSSI.

## Interlocuteurs

- Bartholomé Gillery (DPO de l'académie de Paris) : commanditaire
- Jérôme de Thésut (pôle IA, incubateur) : chef de projet, seul mainteneur
- RSSI de l'académie : validation commune des mesures de sécurité
- DRASI : hébergement de production et authentification

## Documents clés

- Scoring : portefeuille, 024-assistant-pia/SCORING.md
- Carnet de bord : docs/carnet-de-bord.md
- Note de cadrage PIA + MonServiceSécurisé, questions élémentaires, matrice de dépendances : documents Claude partagés avec le DPO
- Table de correspondance des mesures MonServiceSécurisé et PIA (premier jet) : env/review, et page de relecture en ligne partagée avec le DPO

## Points de vigilance

- Données personnelles dans les descriptions et les réponses : envoyées seulement à Albert API ; traitement à inscrire au registre.
- Un seul mainteneur pour trois bases de code (PIA, pia-back, MonServiceSécurisé), dont deux reprises à suivre ; code des adaptations uniquement sur le serveur de développement.
- Quotas Albert partagés (10 requêtes par minute, 1 000 par jour).
- Inscription à MonServiceSécurisé bloquée dans le navigateur à l'étape « Vos consentements » (cause non trouvée).

## Journal

- 2026-11-26 · livrable · Premier jet de la table de correspondance entre les 135 mesures de MonServiceSécurisé et les 29 catégories de mesures du PIA, remis au DPO avec sept questions (PDF et page de relecture en ligne).
- 2026-11-26 · code · Le pré-remplissage du PIA reporte aussi les mesures de MonServiceSécurisé en section 3.1 ; MonServiceSécurisé s'ouvre depuis le parcours sans nouvelle authentification (instance locale).
- 2026-11-26 · décision · Séance DPO : les mesures de MonServiceSécurisé seront rangées dans les catégories de mesures du PIA ; le porteur de projet indiquera dans le parcours si chaque mesure est mise en œuvre.
- 2026-11-26 · réunion · Séance avec le DPO : démonstration du parcours guidé sur un cas de test. Demandes : estimation chiffrée du nombre de personnes concernées, détail des données par catégorie, meilleure correspondance des mesures de sécurité avec celles du PIA.
- 2026-11-20 · code · Délais d'attente allongés après un ralentissement d'Albert qui interrompait l'analyse.
- 2026-11-17 · code · Premier export PDF d'une analyse de test : les brouillons se répétaient à chaque report. Corrigé : report rejouable sans doublon et texte de l'agent conservé, brouillon seulement si l'information principale de la question est connue, chaque risque MonServiceSécurisé rattaché à un seul risque du PIA. Analyse de test nettoyée.
- 2026-11-17 · livrable · Parcours rendu linéaire : le pré-remplissage du PIA se fait à la fin, à l'étape Valider.
- 2026-11-17 · livrable · Étape Valider du parcours : bilan des questions remplies, report des mesures indispensables de MonServiceSécurisé dans le PIA (une fiche par catégorie), liens vers l'avis du DPO, la validation du PIA et l'homologation.
- 2026-11-17 · décision · Scoring réalisé : 65/100, priorité forte. 80/100 si les 5 points à instruire se confirment.
- 2026-11-17 · décision · Fiche de suivi ouverte en phase Prototype : prototype fonctionnel sur le serveur de développement, relu par le DPO.
- 2026-11-17 · livrable · Étape Sécurité du parcours : le service est créé dans MonServiceSécurisé, ses risques et mesures sont relus, les risques sont proposés comme menaces en section 3 du PIA.
- 2026-11-17 · livrable · Parcours guidé des sections 1 et 2 : description libre, propositions d'Albert avec recherche dans Légifrance et les délibérations de la CNIL, pré-remplissage des 18 questions sans écraser l'existant.
- 2026-11-17 · échange · Retours du DPO sur les questions élémentaires et la note de cadrage : option « socle commun et passerelles » retenue, MonServiceSécurisé réservé aux traitements reposant sur un service numérique, validation commune DPO et RSSI pour la sécurité.
- 2026-11-10 · livrable · Installation locale de MonServiceSécurisé (ANSSI) ; note de cadrage PIA et MonServiceSécurisé et questions élémentaires remises au DPO.
- 2026-10-08 · code · Premières fonctions de l'assistant : reformulation des questions, réponses contingentées, contrôles de cohérence entre réponses.
