"""
FILE MAPPER

Analyse la structure du projet pour créer le mapping
entre fichiers source et fichiers de test.

Conventions supportées :
- src/components/Foo.tsx ↔ tests/test_foo.py
- src/components/Foo.tsx ↔ src/__tests__/Foo.test.tsx
- src/utils/bar.ts ↔ tests/test_bar.py
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional
import re
import hashlib
from .models import NeuralConfig


@dataclass
class FileMappingResult:
    source_files: List[Dict]
    test_files: List[Dict]
    connections: List[Dict]
    unmapped_sources: List[str]
    unmapped_tests: List[str]


class FileMapper:
    """Mappe les fichiers source aux fichiers de test."""

    def __init__(self, project_root: str, config: NeuralConfig = None):
        self.root = Path(project_root)
        self.config = config or NeuralConfig()

    def scan_and_map(self) -> FileMappingResult:
        """Scanne le projet et crée le mapping."""
        source_files = self._find_source_files()
        test_files = self._find_test_files()
        connections = self._create_connections(source_files, test_files)

        # Identifier les fichiers non mappés
        mapped_sources = {c['source_id'] for c in connections}
        mapped_tests = {c['test_id'] for c in connections}

        return FileMappingResult(
            source_files=source_files,
            test_files=test_files,
            connections=connections,
            unmapped_sources=[f['path'] for f in source_files if f['id'] not in mapped_sources],
            unmapped_tests=[f['path'] for f in test_files if f['id'] not in mapped_tests]
        )

    def _find_source_files(self) -> List[Dict]:
        """Trouve tous les fichiers source selon la config."""
        import fnmatch
        
        source_files = []
        
        # Utiliser les dossiers définis dans la config
        dirs_to_scan = self.config.source_dirs
        extensions = self.config.file_extensions

        # Patterns d'exclusion OBLIGATOIRES (Performance & Sécurité)
        # On force ces exclusions pour éviter de scanner des millions de fichiers
        forced_excludes = [
            '**/node_modules/**', '**/__pycache__/**', '**/.git/**', 
            '**/target/**', '**/dist/**', '**/build/**', '**/vendor/**', 
            '**/.venv/**', '**/.env', '**/*.d.ts', '**/*.map', '**/*.min.js'
        ]
        
        # Combiner avec les exclusions de test pour éviter les doublons
        all_excludes = forced_excludes + self.config.test_patterns

        # Pré-compiler les regex pour la performance
        exclude_regexes = [re.compile(fnmatch.translate(pat)) for pat in all_excludes]

        for dir_name in dirs_to_scan:
            dir_path = self.root / dir_name
            if not dir_path.exists():
                continue
                
            for ext in extensions:
                # Glob récursif pour l'extension donnée
                pattern = f"**/*{ext}"
                
                try:
                    # Utiliser rglob est plus sûr et plus rapide que glob manuel
                    for file_path in dir_path.rglob(f"*{ext}"):
                        if not file_path.is_file():
                            continue
                            
                        # Chemin relatif pour le matching
                        try:
                            relative_path = str(file_path.relative_to(self.root))
                        except ValueError:
                            continue # Le fichier n'est pas dans root
                        
                        # Vérifier exclusions (Optimisé)
                        if any(regex.match(relative_path) for regex in exclude_regexes):
                            continue

                        # Compter les lignes de code (Robuste)
                        lines = 0
                        try:
                            # Lecture avec fallback d'encodage
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    lines = sum(1 for line in f if line.strip())
                            except UnicodeDecodeError:
                                with open(file_path, 'r', encoding='latin-1') as f:
                                    lines = sum(1 for line in f if line.strip())
                        except Exception:
                            lines = 0 # Fichier illisible ou binaire, on ignore la taille

                        file_id = hashlib.md5(relative_path.encode()).hexdigest()[:8]

                        source_files.append({
                            'id': file_id,
                            'path': relative_path,
                            'name': file_path.name,
                            'extension': file_path.suffix,
                            'linesOfCode': lines,
                            'hasTests': False,
                            'testStatus': 'none'
                        })
                except Exception as e:
                    print(f"⚠ Error scanning directory {dir_path}: {e}")
                    continue

        return source_files

    def _find_test_files(self) -> List[Dict]:
        """Trouve tous les fichiers de test selon la config."""
        test_files = []
        
        dirs_to_scan = self.config.test_dirs
        patterns = self.config.test_patterns

        for dir_name in dirs_to_scan:
            dir_path = self.root / dir_name
            if not dir_path.exists():
                # Try finding tests inside source dirs if dedicated test dir doesn't exist
                if dir_name not in self.config.source_dirs:
                    continue
            
            for pattern in patterns:
                # Glob récursif
                glob_pattern = f"**/{pattern}"
                
                for file_path in dir_path.glob(glob_pattern):
                    if not file_path.is_file():
                        continue
                        
                    relative_path = str(file_path.relative_to(self.root))

                    # Ignorer node_modules et caches
                    if 'node_modules' in relative_path or '__pycache__' in relative_path:
                        continue

                    file_id = hashlib.md5(relative_path.encode()).hexdigest()[:8]

                    test_files.append({
                        'id': file_id,
                        'path': relative_path,
                        'name': file_path.name,
                        'passed': 0,
                        'failed': 0,
                        'skipped': 0,
                        'coverage': 0.0,
                        'lastRun': ''
                    })

        return test_files

    def _create_connections(self, sources: List[Dict], tests: List[Dict]) -> List[Dict]:
        """Crée les connexions entre source et tests."""
        connections = []
        connection_id = 0

        for source in sources:
            source_name = Path(source['name']).stem

            for test in tests:
                test_name = Path(test['name']).stem

                # Stratégies de matching
                matched = False
                strength = 0.0

                # 1. Matching exact (Foo.tsx ↔ Foo.test.tsx)
                if test_name == f"{source_name}.test":
                    matched = True
                    strength = 1.0

                # 2. Matching Python (foo.py ↔ test_foo.py)
                elif test_name == f"test_{source_name}":
                    matched = True
                    strength = 1.0

                # 3. Matching partiel (contient le nom)
                elif source_name.lower() in test_name.lower():
                    matched = True
                    strength = 0.7

                # 4. Matching par chemin similaire
                elif self._path_similarity(source['path'], test['path']) > 0.5:
                    matched = True
                    strength = 0.5

                if matched:
                    connections.append({
                        'id': f"conn_{connection_id}",
                        'source_id': source['id'],
                        'test_id': test['id'],
                        'strength': strength,
                        'status': 'active' if strength > 0.7 else 'weak'
                    })
                    connection_id += 1

                    # Marquer le fichier source comme ayant des tests
                    source['hasTests'] = True

        return connections

    def _path_similarity(self, path1: str, path2: str) -> float:
        """Calcule la similarité entre deux chemins."""
        parts1 = Path(path1).parts
        parts2 = Path(path2).parts

        # Compter les parties communes
        common = 0
        for p1, p2 in zip(parts1, parts2):
            if p1 == p2:
                common += 1
            elif p1.replace('.tsx', '').replace('.ts', '').replace('.py', '') == \
                 p2.replace('.test', '').replace('test_', ''):
                common += 0.5

        max_len = max(len(parts1), len(parts2))
        return common / max_len if max_len > 0 else 0

    def get_mapping_stats(self, result: FileMappingResult) -> Dict:
        """Calcule les statistiques du mapping."""
        total_sources = len(result.source_files)
        total_tests = len(result.test_files)
        mapped_sources = total_sources - len(result.unmapped_sources)
        mapped_tests = total_tests - len(result.unmapped_tests)

        return {
            'total_source_files': total_sources,
            'total_test_files': total_tests,
            'mapped_sources': mapped_sources,
            'mapped_tests': mapped_tests,
            'coverage_percentage': (mapped_sources / total_sources * 100) if total_sources > 0 else 0,
            'strong_connections': len([c for c in result.connections if c['strength'] > 0.7]),
            'weak_connections': len([c for c in result.connections if c['strength'] <= 0.7])
        }