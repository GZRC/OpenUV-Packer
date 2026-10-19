# Phase 2 — premier jalon : MaxRects 0.2.0

19 octobre 2026. Windows x64, Blender 5.2.2 LTS, Zig 0.16.0/Clang 21.1.0,
CMake 4.4.4 et Ninja 1.13.2. Compilation Release via scripts/build-zig.ps1.

## Fonctions livrées

MaxRects propre au projet : BSSF, BAF et Bottom Left ; deux tris, orientations 0/90°,
recherche Fast/Balanced/High et deux workers maximum. Les deux stratégies Shelf sont conservées.
La meilleure échelle Shelf sert de plancher ; chaque résultat est validé avant retour.
Le panneau indique échelle, temps total, aire des rectangles et stratégie réellement utilisée.
Ordre d'extraction des îlots stabilisé pour ne plus dépendre d'un set Python.

Ce jalon ne termine pas toute la phase 2 du cahier des charges : contours et packing polygonal,
Skyline, recherche locale et limite de temps configurable restent à développer. Aucun GPU.

## Tests exécutés et réussis

- CMake/CTest : **3/3**. Ancienne géométrie, auto-test CLI et suite MaxRects.
- MaxRects : optima analytiques simples, marges, rotations désactivées/activées,
  12 corpus aléatoires avec deux réglages de marge, deux réglages de rotation, trois qualités,
  comparaison au plancher Shelf et correspondance exacte entre exécution série et parallèle.
  Cas très allongés, grandes marges impossibles, collision volontaire, seuils 128/256/512 et fallback à 513.
  La vérification de ces tests est une comparaison indépendante de toutes les paires de rectangles.
- Python : **6/6**, avec 28 appels de packing sur 1 à 10000 îlots, entrées invalides,
  déterminisme, protocole, qualités et comparaison à Shelf. Pour les grands lots, fallback Shelf explicite.
- Blender headless : **OPENUV_BLENDER_SMOKE_OK**. Îlots, sync/non-sync, moteurs Python/C++,
  statistiques, refus des UV épinglés, Undo/Redo et géométrie 3D inchangée.
- Scène réelle : **OPENUV_REAL_MESH_OK** sur le pied de 9596 faces et 51 îlots.
  Validation après stockage des UV en float32, séparation avec marges à 1e-6,
  géométrie 3D inchangée et restauration exacte des UV par Undo. Le fichier source n'a pas été enregistré.
- ZIP 0.2.0 : **OPENUV_PACKAGE_OK**. Extraction du ZIP, activation de l'add-on, vérification
  de la version et du mode High avec 8 recherches, packing natif puis désactivation.
  Avertissement de cache Extensions Blender non inscriptible dans le bac à sable, sans échec du test.

Logs finaux dans docs/logs/phase2-*.txt. L'apparence du panneau n'a pas été contrôlée visuellement.
Blender 4.5 et d'autres machines/CPU restent non testés. MSVC n'est pas installé ici.

## Benchmark du modèle utilisateur

Neuf maillages extraits de la version sauvegardée du fichier montré dans les captures.
Seuls des résumés de mesures sont publiés, pas la scène ni les dimensions détaillées des îlots.
Le benchmark compare les mêmes rectangles, dans le même ordre stable, par `--shelf` et le portefeuille.
Balanced, rotations autorisées, marge affichée 0.0020 (valeur float32 réelle : 0.0020000000949949026).
Trois répétitions par stratégie. Temps CLI avec démarrage du processus et vérification Python inclus ;
extraction et application Blender exclues. Ce sont des mesures locales, pas une garantie générale.

| Objet | Îlots | Échelle Shelf | Échelle 0.2.0 | Gain de longueur relatif | Temps médian 0.2.0 (s) |
|---|---:|---:|---:|---:|---:|
| ailes | 93 | 0.83543 | 0.89889 | 7.60 % | 0.0479 |
| bras | 35 | 1.19847 | 1.31029 | 9.33 % | 0.0137 |
| brase3d | 215 | 0.83670 | 0.89153 | 6.55 % | 0.3406 |
| corps | 56 | 0.82768 | 0.89267 | 7.85 % | 0.0203 |
| jambes | 46 | 1.19121 | 1.30752 | 9.76 % | 0.0151 |
| main | 55 | 0.81853 | 0.89174 | 8.94 % | 0.0200 |
| pied | 51 | 0.86774 | 0.91078 | 4.96 % | 0.0179 |
| TAIL | 33 | 0.94828 | 1.03144 | 8.77 % | 0.0134 |
| tête | 181 | 0.83556 | 0.88440 | 5.84 % | 0.2109 |

Sur le pied, le test complet dans Blender donne **0.91078**, contre **0.86774** pour Shelf.
Les longueurs sont réduites de 8.92 % au lieu de 13.23 % ; c'est un gain relatif d'environ 4.96 %
par rapport à l'échelle Shelf. L'opération complète Blender a pris environ 0.195 s lors du dernier
contrôle, une seule exécution (extraction et application incluses). L'aire des rectangles après
packing est de 89.6 % ; cela ne représente pas l'occupation réelle des triangles UV.
Une première mesure avec marge double exactement 0.002 donnait 0.91225 : de petites variations
numériques peuvent changer les décisions d'une heuristique. Les résultats finaux ci-dessus utilisent
la marge réellement stockée par Blender et un ordre d'îlots stable.

## Benchmark synthétique

Graine 51, côtés uniformes entre 0.01 et 1, marge double 0.002 et trois répétitions.
Entrées régénérables par scripts/benchmark_phase2.py. Aucun cas de la table ne régresse en échelle.

| Îlots | Échelle Shelf | Échelle 0.2.0 | Gain relatif | Temps médian 0.2.0 (s) |
|---:|---:|---:|---:|---:|
| 10 | 0.48090 | 0.52317 | 8.79 % | 0.0097 |
| 51 | 0.21730 | 0.22525 | 3.66 % | 0.0197 |
| 100 | 0.18034 | 0.18987 | 5.28 % | 0.0569 |
| 256 | 0.11420 | 0.11694 | 2.40 % | 0.5799 |
| 1000 | 0.05265 | 0.05265 | 0.00 % | 0.0329 |
| 10000 | 0.01172 | 0.01172 | 0.00 % | 0.5657 |

Les lots de 1000 et 10000 îlots dépassent le seuil Balanced : retour Shelf déclaré, donc aucun gain.
Les temps sont spécifiques à cette machine et à ces données. Aucun benchmark GPU, aucune mesure mémoire,
aucune comparaison avec Blender Pack Islands ou UVPackmaster. La recherche supplémentaire peut coûter
plus de temps que Shelf ; aucune accélération globale n'est annoncée.

## Reproduire

```powershell
./scripts/build-zig.ps1 -Zig '<chemin>/zig.exe' -CMake '<chemin>/cmake.exe' -Ninja '<chemin>/ninja.exe'
./scripts/test.ps1 -Python python -Blender '<chemin>/blender.exe'
python scripts/benchmark_phase2.py --repeats 3 > benchmarks/local-phase2.json
./scripts/package.ps1
blender --background --factory-startup --python-exit-code 1 --python tests/package_smoke.py
```

Les commandes d'extraction et de test du modèle sont décrites dans les en-têtes des scripts correspondants.
Les résultats JSON complets sont dans benchmarks/phase2-model.json et phase2-synthetic.json.

## Limites et suite

Rectangles englobants, une seule tuile, un seul objet. Îlots épinglés refusés ; faces cachées et UV
non sélectionnés exclus ; aucun obstacle fixe. Les auto-chevauchements internes ne sont pas réparés.
Pas de contours concaves/trous exploités, pas d'optimum garanti. Prochaine étape : géométrie polygonale
robuste et placement selon les contours, avant UDIM/contraintes puis Vulkan.
