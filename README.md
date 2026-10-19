# OpenUV Packer 0.2.0 — MaxRects CPU

Add-on Blender gratuit, GPL-3.0-or-later. Moteur C++20 propre au projet ;
aucune dépendance à UVPackmaster, Xatlas ou UVAtlas. Utilisation hors ligne, sans télémétrie.

[Télécharger le ZIP installable](dist/OpenUV-Packer-addon.zip) : utiliser **Download raw file**.

## Installation

1. Blender → Édition → Préférences → Installer depuis un disque : sélectionner le ZIP intact.
2. Activer OpenUV Packer ; après une mise à jour, redémarrer Blender. Le panneau doit afficher **0.2.0**.
3. Sélectionner un seul maillage en mode Édition, avec une UV map.
4. Dans l'éditeur UV, sélectionner les îlots, puis **N → OpenUV → Pack OpenUV**.

Les îlots visibles partiellement sélectionnés sont traités en entier. Pour tout packer, sélectionner
toutes les faces/UV visibles. Les UV non sélectionnés ne sont pas des obstacles.
Le packing déplace les UV et peut donc désaligner une texture existante : tester sur une copie.
Blender 5.2.2 a été testé ; Blender 4.5 LTS reste la cible initiale à vérifier.

## Nouveautés 0.2.0

- MaxRects C++ : BSSF (ajustement au petit côté), BAF (aire libre), Bottom Left.
- Deux ordres stables : aire et plus grand côté, rotations 0/90° évaluées au placement.
- Le meilleur placement des deux variantes de l'ancien moteur Shelf reste candidat.
  Le résultat retenu ne diminue donc pas l'échelle de cette référence, à données et marge identiques.
- Recherche CPU limitée à deux workers ; sélection déterministe pour une entrée identique.
- Contrôle natif des limites et des collisions, puis seconde vérification dans le pont Python.
- Statistiques : temps total de l'opération Blender, échelle commune appliquée, aire des rectangles
  hors marges, moteur et stratégie retenue. L'aire affichée n'est **pas** une occupation polygonale.
- Marge affichée avec quatre décimales ; interface corrigée depuis 0.1.1.

| Qualité C++ | Recherches MaxRects | Heuristiques | Limite d'îlots |
|---|---:|---|---:|
| Fast | 2 | BSSF, deux tris | 128 |
| Balanced | 4 | BSSF + BAF, deux tris | 256 |
| High | 6 | BSSF + BAF + Bottom Left, deux tris | 512 |

Les deux recherches Shelf sont ajoutées à ces nombres. Au-delà de la limite du préréglage,
le moteur utilise Shelf et le signale dans ses statistiques. Ces limites concernent les **îlots**,
pas le nombre de triangles : un maillage high poly de 51 îlots peut bénéficier de MaxRects.
L'interface est synchrone ; le timeout du processus natif est de 120 secondes, pas une limite de recherche configurable.

**Auto** : C++ si le binaire est présent, sinon secours Python Shelf. **Python CPU** reste l'algorithme
historique, sans MaxRects ; son réglage de qualité est sans effet. Un binaire natif présent mais défaillant
produit une erreur explicite. Aucun mode GPU factice.

## Marges et géométrie

Une marge m est réservée par côté du rectangle : au moins 2m entre îlots et m au bord de la tuile.
L'échelle est commune, les proportions et l'échelle relative des îlots sont conservées.
Une échelle 0.9 signifie une réduction de 10 % des longueurs UV, pas de 10 % de l'aire.
Le moteur distingue les îlots par continuité UV des deux extrémités des arêtes du maillage.
L'opération prend en charge Undo/Redo et ne change pas les coordonnées 3D.

Les faces cachées sont exclues ; les arêtes non manifold délimitent les îlots.
UV épinglés, dimensions nulles et édition multi-objets sont refusés.
La séparation est vérifiée entre les rectangles des îlots traités, pas à l'intérieur d'un même îlot :
les auto-chevauchements préexistants ne sont pas réparés. Seule la tuile 1001 ([0,1]²) est utilisée.
Tolérances : 1e-9 pour la validation double, 1e-6 dans les tests après stockage float32 Blender.

## Compiler et tester

CMake ≥ 3.20, compilateur C++20 et Windows x64. Avec MSVC installé :

```powershell
./scripts/build.ps1
./scripts/test.ps1 -Python python -Blender 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
./scripts/package.ps1
```

La voie réellement exécutée sur cette machine est **Zig + CMake + Ninja** :
voir [BUILD.md](docs/BUILD.md). `scripts/build-zig.ps1` compile OpenUVCore, le CLI et les tests,
exécute CTest, puis installe le binaire dans `addon/bin`. `scripts/package.ps1` génère le ZIP
à côté du dépôt. Pour actualiser la copie publique :

```powershell
Copy-Item ../OpenUV-Packer-addon.zip dist/OpenUV-Packer-addon.zip -Force
```

## Mesures et tests

[Rapport 0.2.0](docs/PHASE2_REPORT.md), [rapports historiques](docs/TEST_REPORT.md).
Les mesures comparent les mêmes rectangles avec `--shelf` et le portefeuille MaxRects,
avec trois répétitions. Elles ne constituent pas une comparaison à Blender Pack Islands ou UVPackmaster.

```powershell
python scripts/benchmark_phase2.py --repeats 3 > benchmarks/local-phase2.json
```

Le script optionnel `scripts/extract_benchmark_blender.py` extrait des dimensions depuis une scène
sans la sauvegarder. Les tests `tests/blender_real_mesh.py` sont également réalisés en mémoire.
Le modèle utilisateur n'est pas inclus au dépôt ; seuls les résumés chiffrés sont publiés.

## État de la phase 2 et limites

Cette version livre le **premier jalon de la phase 2 : MaxRects et statistiques**.
Les îlots concaves et les trous restent représentés par leur rectangle englobant.
**Non implémentés** : extraction des contours polygonaux, placement polygonal, NFP, Skyline,
recherche locale/annealing, limite de temps configurable, densité absolue des texels,
unités pixels, UDIM, verrouillages/obstacles, groupes, empilement, priorités, Vulkan,
occupation polygonale réelle, mesure mémoire et comparaison à Blender Pack Islands.
Aucun optimum mathématique n'est garanti. Voir [ROADMAP.md](docs/ROADMAP.md).

## Sources

`addon/` : opérateurs, panneau, propriétés et pont Python (paquet `openuv_packer` dans le ZIP).
`engine/include` et `engine/src` : bibliothèque OpenUVCore et CLI.
`engine/algorithms`, `engine/geometry`, `engine/cpu` : MaxRects, validation et recherche.
`tests/`, `benchmarks/`, `scripts/`, `docs/` : vérification, mesures et documentation.

Copyright (C) 2026 OpenUV Packer contributors. GPL version 3 ou ultérieure ; aucune garantie.
Voir LICENSE.
