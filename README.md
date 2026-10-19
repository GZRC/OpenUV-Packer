# OpenUV Packer — phase 1, version 0.1.0

Add-on Blender gratuit sous **GPL-3.0-or-later**, sans moteur externe de packing.
Algorithmes propres au projet ; aucune dépendance à UVPackmaster, Xatlas ou UVAtlas.
Aucune connexion requise à l’utilisation. Pas de télémétrie.

[Télécharger le ZIP installable](dist/OpenUV-Packer-addon.zip) (Download raw file).

## Installer

1. Télécharger/décompresser `OpenUV-Packer-addon.zip` seulement si vous souhaitez inspecter son contenu ; pour installer, conserver le ZIP intact.
2. Blender : Édition → Préférences → Extensions/Add-ons → menu → Installer depuis un disque ; choisir le ZIP, puis activer OpenUV Packer.
3. Créer une UV map, passer en mode Édition, ouvrir l’éditeur UV et sélectionner les îlots.
4. Barre latérale (N) → OpenUV → Pack OpenUV.
5. Pour tout packer, sélectionner toutes les faces/UV visibles avant l’opération.

Le ZIP inclut le moteur Windows x64 lorsqu’il a été compilé. Auto utilise le C++ présent,
sinon le moteur Python de secours. Les modes C++ et Python peuvent donner des placements
différents ; chacun est validé avant application. L’UI indique le moteur effectivement utilisé.
Blender 4.5 LTS est la cible initiale ; consulter `docs/TEST_REPORT.md` pour les versions réellement testées.

## Fonctions de cette phase

- Îlots connexes par arêtes du maillage et continuité des deux extrémités UV (tolérance 1e-7).
- Une sélection partielle étendue à l’îlot visible complet ; sync de sélection pris en compte.
- Rectangles englobants, placement par étagères, deux ordres de tri, recherche d’une échelle commune.
- Rotation optionnelle 0/90°, conservation de l’échelle relative et des proportions.
- Marge UV par côté de rectangle : une valeur m crée au moins 2m entre îlots et m au bord.
- Validation des dimensions, des résultats finis, des limites de tuile et des intersections de rectangles.
- Refus des îlots épinglés, des UV dégénérés et de l’édition multi-objets.
- Opérateur Blender enregistré pour Undo/Redo ; aucune modification de la géométrie 3D.
- OpenUVCore indépendant de Blender ; moteur CLI C++20 ; deux recherches CPU concurrentes dans le CLI.

## Compiler sous Windows x64

Installer CMake ≥ 3.20 et Visual Studio Build Tools avec la charge C++.
Depuis PowerShell dans ce dépôt :

```powershell
./scripts/build.ps1
./scripts/test.ps1 -Python python -Blender 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
./scripts/package.ps1
```

Ou utiliser CMake directement :

```powershell
cmake -S . -B build
cmake --build build --config Release
ctest --test-dir build -C Release --output-on-failure
cmake --install build --config Release --prefix .
```

Voir `docs/BUILD.md` pour la chaîne portable employée lors de cette livraison.
La bibliothèque statique `OpenUVCore` est construite séparément de `openuv_engine`.
L’exécutable est installé dans `addon/bin`. Aucun paquet Python externe n’est requis.

## Tests et mesures

```powershell
python tests/test_packing.py
python scripts/benchmark.py > benchmarks/local.json
```

Tests natifs via CTest, tests Blender sans interface via `scripts/test.ps1`.
Les benchmarks utilisent des rectangles synthétiques et mesurent une seule exécution :
ils ne prouvent ni une occupation polygonale réelle ni une accélération face à un autre produit.
Les résultats exécutés et leurs limites figurent dans `docs/TEST_REPORT.md`.

## Limites importantes

**Phase 1 uniquement.** Placement conservateur par rectangles, sans optimum garanti.
Les formes concaves et trous ne sont pas exploités : ils occupent leur rectangle englobant.
Le packer empêche les intersections entre rectangles des îlots traités, mais ne corrige pas
les UV déjà auto-superposés à l’intérieur d’un même îlot. Les éléments non sélectionnés
ne sont pas des obstacles ; sélectionner tous les îlots pour valider l’ensemble d’une tuile.
Les faces cachées sont exclues. Les arêtes non manifold sont des frontières d’îlots.
Les UV de largeur ou hauteur nulle sont refusés. Seule la tuile [0,1]² (1001) est utilisée.
L’appel est synchrone et peut bloquer l’interface sur de gros maillages ; timeout natif 120 s.
Le validateur utilise une tolérance de 1e-9 en double ; les UV Blender sont stockés en float32.
La vérification après écriture dans Blender utilise une tolérance distincte de 1e-6.

Non implémentés : MaxRects, skyline, packing polygonal, NFP, recherche locale/annealing,
limite de temps configurable, niveaux de qualité, densité absolue des texels, unités pixels,
UDIM, obstacles verrouillés, groupes, empilement, priorités, statistiques polygonales,
Vulkan Compute, identification GPU, comparaison à Blender Pack Islands, mesures mémoire.
Aucun bouton GPU factice n’est présenté. Voir `docs/ROADMAP.md`.

## Organisation

`addon/` : sources du paquet installable (renommé `openuv_packer` dans le ZIP), opérateur,
panneau, propriétés, pont et secours Python. `engine/include` et `engine/src` : bibliothèque
et CLI. `tests` : géométrie, refus et intégration Blender. `scripts` : build, test, package,
benchmark. `benchmarks` : résultats mesurés. `docs` : spécification, architecture, rapports.
Les dossiers réservés aux phases suivantes sont documentés et ne contiennent pas de faux backend.

Copyright (C) 2026 OpenUV Packer contributors. Redistribution et modification selon
GPL version 3 ou ultérieure. Aucune garantie. Texte complet dans LICENSE.
