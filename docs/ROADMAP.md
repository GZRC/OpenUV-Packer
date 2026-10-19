# Feuille de route

1. **Phase 1 — livrée (0.1.x)** : îlots, rectangles, marges, rotation, C++ indépendant, Undo/Redo, ZIP et tests.
2. **Phase 2 — en cours (0.2.0)** : MaxRects propre au projet, BSSF/BAF/Bottom Left, recherche configurable,
   baseline Shelf, validations et statistiques. Prochain jalon : contours, trous, géométrie robuste,
   placement polygonal et tests adverses, puis Skyline et recherche locale. La phase 2 complète du cahier
   des charges n'est donc pas encore achevée.
3. **Phase 3** : UDIM, obstacles verrouillés, groupes, empilement et conservation des overlaps intentionnels.
4. **Phase 4** : Vulkan effectif (appareils, buffers, collisions, synchronisation), comparaison CPU/GPU,
   tolérances, fallback et benchmarks avant toute annonce d'accélération.
5. **Phase 5** : mémoire, corpus réel, comparaisons contrôlées à Blender Pack Islands, ergonomie,
   annulation et optimisation à partir des mesures.

Le high poly exige des tests d'extraction/application en plus du benchmark de packing :
les coûts en faces et en îlots doivent être distingués.
