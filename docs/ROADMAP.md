# Feuille de route et critères de passage

1. **CPU MVP** : add-on installable, îlots, étagères, rotation, marges, tests natifs et Blender, preuve de compilation et ZIP. Compléter la validation Blender 4.5, les scènes réelles et les limites numériques.
2. **C++ avancé** : contours orientés, trous et validation géométrique, intersection robuste, MaxRects/Skyline, placement polygonal, heuristiques puis recherche configurable. Référence CPU et jeux de tests adverses avant toute promesse.
3. **UDIM et contraintes** : attribution des tuiles, obstacles épinglés, groupes, empilement explicite, conservation des overlaps voulus ; tests de non-régression.
4. **Vulkan** : détection des appareils, buffers, shaders de collision/évaluation, synchronisation, fallback CPU. Comparer décisions et géométrie CPU/GPU avec tolérances avant benchmark. Aucun backend implémenté dans la phase 1.
5. **Optimisation** : benchmarks répétés, mémoire et corpus de scènes, comparaison à Blender sur données identiques, ergonomie et annulation asynchrone.

Chaque phase doit fournir code, tests, compilation, documentation et rapport honnête.
