# Compilation Windows

La voie standard est `scripts/build.ps1` avec CMake et MSVC installés ; MSVC n'était pas
disponible sur la machine de livraison. Ce chemin n'a donc pas été exécuté ici.

La compilation réellement exécutée utilise Windows x64, Zig 0.16.0 (Clang 21.1.0),
CMake 4.4.4 et Ninja 1.13.2, téléchargés comme outils de développement dans `work/toolchain`.
Ces outils ne sont pas requis pour utiliser l'add-on et ne sont pas inclus dans le ZIP.

Une autre machine peut préparer ses outils (connexion nécessaire uniquement pour ce téléchargement) :

```powershell
python -m pip install --target .tools ziglang==0.16.0 cmake==4.4.4 ninja==1.13.2
./scripts/build-zig.ps1 -Zig "$PWD/.tools/ziglang/zig.exe" -CMake "$PWD/.tools/cmake/data/bin/cmake.exe" -Ninja "$PWD/.tools/bin/ninja.exe"
./scripts/package.ps1
```

La première compilation de la bibliothèque standard de Zig peut prendre plusieurs minutes.
Les avertissements de nullabilité dans la bibliothèque standard fournie avec Zig ont été observés.
Les fichiers de cache sont placés dans le dossier de build. Les binaires sont testés sur cette
machine seulement ; aucune validation sur d'autres CPU Windows ni sur Linux/macOS.

OpenUVCore est une bibliothèque statique C++20. L'exécutable CLI est copié dans `addon/bin`.
La distribution source contient toute la source de l'add-on et du moteur, les scripts et la licence.
Les commandes `scripts/test.ps1` et `ctest` sont indépendantes de l'interface Blender.
