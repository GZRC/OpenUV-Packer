# Architecture phase 1

Le collecteur BMesh travaille sur le maillage actif en mode Édition. Un graphe de faces visibles
connecte deux faces seulement si les UV des extrémités de leur arête commune coïncident.
Le packer reçoit uniquement les dimensions des rectangles ; pas de données Blender dans OpenUVCore.

OpenUVCore expose `solve(boxes, margin, rotate, strategy)` ; le CLI lance deux stratégies en parallèle
avec std::async et conserve celle qui produit l’échelle la plus grande. Chaque stratégie emploie
un ordre stable (aire ou plus grand côté), une orientation portrait optionnelle et un placement
par étagères. Une recherche dichotomique de 64 tours cherche une échelle admissible. La recherche
n’est pas une preuve d’optimalité : la faisabilité d’une heuristique avec changements de rangées
peut être non monotone. Un placement final est recalculé et contrôlé par le pont.

Protocole CLI v0.1 sur stdin/stdout, nombres décimaux avec point :
`nombre marge rotation workers`, puis `largeur hauteur` par îlot. Sortie : échelle, puis
`x y rotation` par îlot dans l’ordre d’entrée. Erreurs stderr + code 2. Rotation vaut 0 ou 1 ;
workers > 1 active deux recherches. Indices implicites par ordre. Limite 100000 rectangles.
Le pont Python valide les résultats avant de calculer toutes les coordonnées, puis applique
la transformation à l’ensemble des loops. Une rotation est (u,v) → (hauteur-v,u), puis échelle
commune et translation. Les faces cachées et données non sélectionnées restent hors calcul.

Le CLI permet d’éviter une dépendance ABI à la version Python de Blender. L’appel subprocess
est sans shell, local et limité à 120 secondes ; un échec du moteur est affiché explicitement.
Auto utilise Python si le binaire est absent. Un binaire présent mais défaillant déclenche une erreur,
pas un changement de moteur silencieux. Vulkan et les contraintes exigeront une version ultérieure
du protocole, transportant contours, trous et obstacles.

API Blender vérifiée par exécution locale et documentation officielle :
https://docs.blender.org/api/5.0/bmesh.html
Les propriétés UV select ont changé en 5.2 ; adaptation par détection de capacité.
