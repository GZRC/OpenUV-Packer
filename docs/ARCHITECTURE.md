# Architecture 0.2.0

## Intégration Blender

Le collecteur BMesh connecte les faces visibles si les UV des deux extrémités de leur arête
commune correspondent à 1e-7. L'ordre des îlots suit maintenant l'ordre stable des faces,
plutôt que les adresses d'allocation d'un ensemble Python. Une sélection partielle est étendue
à l'îlot visible entier. Pas de modification des faces cachées ni des objets non actifs.

Le pont envoie seulement les dimensions des rectangles à un processus CLI local, sans shell.
Il vérifie les résultats avant d'appliquer une rotation 0/90°, une échelle uniforme et une translation.
Le timeout est de 120 secondes. Auto ne bascule sur Python que si le binaire C++ est absent.
Le fallback Python conserve Shelf et n'exécute pas MaxRects.

## OpenUVCore

Bibliothèque statique indépendante de Blender. `solve` conserve le moteur Shelf historique,
avec deux ordres de tri. `solve_best` retient le meilleur Shelf comme plancher, puis lance
le portefeuille MaxRects dans au plus deux workers. Fast/Balanced/High sélectionnent respectivement
2/4/6 recherches MaxRects et 20/28/36 raffinements, avec limites de 128/256/512 îlots.
Au-delà : Shelf, indiqué explicitement. Une fragmentation dépassant 4096 rectangles libres
abandonne le candidat concerné et conserve le plancher.

MaxRects maintient des rectangles libres, considère les orientations autorisées, puis classe
les emplacements par petit côté restant, aire libre ou position basse/gauche. Après insertion,
chaque rectangle libre intersecté est découpé ; les rectangles contenus dans d'autres sont supprimés.
Les zones libres peuvent se recouvrir entre elles, sans recouvrir une zone occupée.
Implémentation écrite pour ce projet, sans bibliothèque de packing externe. Référence publique :
Jukka Jylänki, *A Thousand Ways to Pack the Bin* (2010), disponible dans
https://github.com/juj/RectangleBinPack (rapport PDF). Aucun code de ce dépôt n'est lié ou incorporé.

La borne de recherche utilise l'aire et le plus grand côté. Huit sondes dans l'intervalle
au-dessus du plancher précèdent une recherche dichotomique. La faisabilité d'une heuristique
n'étant pas nécessairement monotone, il ne s'agit pas d'une preuve d'optimum.
Les placements réellement réussis sont conservés ; ils ne sont pas recalculés à une échelle
voisine pour la validation. Une légère réduction à origines fixes protège les frontières numériques.
Le résultat final est contrôlé par un balayage des rectangles avec une tolérance de 1e-9,
puis par un second validateur indépendant côté Python. Les tests C++ MaxRects utilisent
également une vérification indépendante par toutes les paires.

## Protocole CLI

En-tête stdin : `n marge rotation workers [qualité]`, suivi d'une ligne `largeur hauteur`
par îlot. Qualité optionnelle : 0 Fast, 1 Balanced (défaut), 2 High. Rotation 0/1, workers ≥ 1.
Deux workers maximum, même si un nombre supérieur est demandé. Limite générale : 100000 rectangles.
Sortie stdout : échelle sur une ligne, puis `x y rotation` par îlot dans l'ordre d'entrée.
Métadonnées stderr : `OPENUV algorithme nombre_recherches maxrects_ignoré`, où le dernier champ est 0/1.
Échec : stderr et code 2, sans résultat partiel. `--shelf` force la référence historique,
`--version` affiche la version et `--self-test` exécute le test rapide.
Le pont 0.2.0 et son binaire doivent être mis à jour ensemble : installer le ZIP complet.

## Statistiques

Temps total Blender mesuré depuis le début de l'opération jusqu'à la mise à jour des UV :
extraction, moteur, communication, validation et application inclus. Ce n'est pas un temps GPU.
L'aire est la somme des aires des rectangles d'origine multipliée par l'échelle au carré,
hors marges. Ce n'est ni l'aire des triangles ni une statistique d'occupation polygonale réelle.
Les statistiques sont celles de la dernière opération, sans sauvegarde persistante, et reviennent
avec l'état Blender lors de Undo/Redo. Aucun calcul GPU n'est exécuté.
