# Rapport de livraison — Phase 1

Date : 19 octobre 2026. Phase 1 réalisée et testée sur la machine locale ; les phases 2–5 restent à développer.

## Environnement et compilation

Windows x64 ; Blender 5.2.2 LTS (build d13f752e3b9c, 15 septembre 2026).
Blender 4.5 n'est pas installé : compatibilité non validée par exécution.
Python de développement fourni avec l'environnement Codex ; Python Blender pour l'intégration.
Aucun compilateur C++ ni CMake initialement dans PATH. Chaîne portable installée localement :
Zig 0.16.0 / Clang 21.1.0, CMake 4.4.4, Ninja 1.13.2.

Compilation Release de la bibliothèque statique OpenUVCore, du CLI et des tests : **réussie**.
Le script livré `scripts/build-zig.ps1` a été exécuté jusqu'à la construction, CTest et l'installation.
La variante MSVC `scripts/build.ps1` n'a pas été exécutée (MSVC indisponible).
Des essais initiaux ont échoué sur les permissions temporaires du bac à sable puis sur la
configuration de l'archiveur ; la construction validée utilise des caches locaux et déclare
explicitement `zig ar` / `zig ranlib`. Avertissements observés dans la bibliothèque standard Zig.

## Résultats réels

- CTest : **2/2 réussis**, tests OpenUVCore et CLI. Corpus natif de 1, 10, 100, 1000 rectangles,
  deux tris et deux réglages de rotation ; validation des bords, marges et collisions, entrées invalides.
- Python : **5/5 réussis**, dont 28 appels de packing sur 1, 2, 5, 10, 100, 1000 et 10000 rectangles
  avec/sans rotation et moteurs Python/Auto (C++ présent). Vérification des résultats, répétabilité,
  collision volontaire, entrées dégénérées/NaN et quatre entrées CLI malformées.
- Blender headless : **OPENUV_BLENDER_SMOKE_OK**. Deux faces connectées : un îlot ; après décalage UV :
  deux îlots. Packing Python et C++, sélection sync et non sync, limites de tuile et séparation.
  UV épinglés refusés sans modification. Undo restaure les UV, Redo les réapplique ; coordonnées 3D inchangées.
- ZIP : **OPENUV_PACKAGE_OK**. Extraction dans un dossier temporaire du projet, activation via addon_utils,
  packing d'un cube avec le C++ inclus, désactivation. Le passage manuel par le menu d'installation et
  l'affichage du panneau n'ont pas été vérifiés visuellement. Un avertissement de cache Extensions
  Blender non inscriptible dans le bac à sable a été émis, sans échec du test.

Les logs des exécutions finales sont joints dans docs/logs/.

## Mesures synthétiques reproductibles

Graine 42 ; rectangles uniformément tirés entre 0.01 et 1 ; marge par côté 0.0005 ; rotation active.
Une seule exécution par cas, sur cette machine, avec concurrence possible d'autres tests.
Temps de l'appel `pack` avec validation et, en C++, démarrage/communication du processus inclus.
Une seconde validation est exécutée hors chronométrage. Pas de mesure mémoire ni GPU.
L'aire indiquée est celle des rectangles hors marges, pas l'occupation réelle de polygones.
Aucune comparaison à Blender Pack Islands ou à UVPackmaster n'a été exécutée.

| Îlots | Moteur | Temps (s) | Aire des rectangles / tuile |
|---:|---|---:|---:|
| 10 | Python CPU | 0.001626 | 0.596528 |
| 10 | C++ CPU (2 searches) | 0.065186 | 0.596528 |
| 100 | Python CPU | 0.015542 | 0.851169 |
| 100 | C++ CPU (2 searches) | 0.027514 | 0.851169 |
| 1000 | Python CPU | 0.157592 | 0.895723 |
| 1000 | C++ CPU (2 searches) | 0.053401 | 0.895723 |
| 10000 | Python CPU | 2.326035 | 0.795754 |
| 10000 | C++ CPU (2 searches) | 0.644476 | 0.795754 |

Ces mesures sont un point de départ, sans garantie de vitesse sur d'autres modèles ou matériels.
Les jeux convexes/concaves, trous, scènes réelles, UDIM et contraintes ne sont pas encore testés.
La correction démontrée concerne la séparation des rectangles des îlots traités ; les auto-overlaps
internes à un îlot ne sont pas réparés. Sélectionner tous les îlots pour inclure tous les obstacles.

## Suite prioritaire

Valider Blender 4.5 et l'installation manuelle, enrichir le corpus de maillages et les cas numériques,
puis phase 2 : extraction polygonale robuste et heuristiques supplémentaires.
Voir ROADMAP.md et README.md pour toutes les fonctions absentes.
