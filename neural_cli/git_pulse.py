"""
GIT PULSE ENGINE

Analyse l'historique Git en temps réel et génère des événements
visuels pour le frontend.

Fonctionnalités :
1. Détection des nouveaux commits (polling toutes les 5 secondes)
2. Analyse des fichiers modifiés par commit
3. Détection des branches actives
4. Génération d'événements "pulse" pour les animations
"""

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Callable, Awaitable
import subprocess
import asyncio
from pathlib import Path
import json
import re
import os


@dataclass
class CommitPulse:
    """Représente un événement de commit pour l'animation."""
    hash: str
    author: str
    message: str
    timestamp: datetime
    files_changed: List[str]
    insertions: int
    deletions: int
    intensity: float  # 0-1, calculé selon l'impact du commit


@dataclass
class BranchActivity:
    """Activité sur une branche."""
    name: str
    is_active: bool
    last_commit: datetime
    commits_ahead: int
    color: str  # Couleur assignée pour la visualisation


@dataclass
class FileHeat:
    """Fréquence de modification d'un fichier."""
    path: str
    modification_count: int
    last_modified: datetime
    heat_level: float  # 0-1


class GitPulseEngine:
    """
    Moteur d'analyse Git pour générer des animations.

    Usage:
        engine = GitPulseEngine("/path/to/repo")
        await engine.start()

        # Les événements sont envoyés via callback
        engine.on_pulse = lambda pulse: broadcast_to_clients(pulse)
    """

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.last_commit_hash: Optional[str] = None
        self.on_pulse: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None
        self.on_branch_activity: Optional[Callable[[List[BranchActivity]], Awaitable[None]]] = None
        self.running = False

        # Vérifier si c'est un dépôt Git
        if not (self.repo_path / ".git").exists():
            print(f"⚠ Warning: {repo_path} is not a Git repository")
            # Initialiser Git si nécessaire
            self._init_git_repo()

    def _run_git_command(self, cmd: List[str], capture_output: bool = True, text: bool = True, check: bool = True) -> subprocess.CompletedProcess:
        """Helper to run git commands with non-interactive SSH."""
        env = os.environ.copy()
        env["GIT_SSH_COMMAND"] = "ssh -o BatchMode=yes"
        try:
            return subprocess.run(
                cmd,
                cwd=str(self.repo_path),
                capture_output=capture_output,
                text=text,
                check=check,
                env=env
            )
        except subprocess.CalledProcessError as e:
            # Log the error but don't re-raise for non-critical git info commands unless check=True was passed and handled by caller
            if check:
                raise e
            print(f"⚠ Git command failed: {' '.join(cmd)}. Error: {e.stderr.strip() if e.stderr else 'unknown'}")
            # Return a dummy failed process object so callers don't crash if they don't catch exception
            return subprocess.CompletedProcess(args=cmd, returncode=1, stdout="", stderr=str(e))

    def _init_git_repo(self):
        """Initialise un dépôt Git s'il n'existe pas."""
        try:
            self._run_git_command(["git", "init"], check=True)
            print(f"✓ Git repository initialized at {self.repo_path}")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to initialize Git repository")

    async def start(self):
        """Démarre le polling Git."""
        self.running = True
        self.last_commit_hash = self._get_latest_commit_hash()

        if self.last_commit_hash:
            print(f"🎯 Git Pulse Engine started. Latest commit: {self.last_commit_hash[:8]}")
        else:
            print("🎯 Git Pulse Engine started. No commits yet.")

        while self.running:
            try:
                await self._check_for_changes()
            except Exception as e:
                print(f"⚠ Git Pulse error: {e}")

            await asyncio.sleep(5)  # Poll toutes les 5 secondes

    def stop(self):
        """Arrête le polling."""
        self.running = False
        print("🛑 Git Pulse Engine stopped")

    async def _check_for_changes(self):
        """Vérifie les nouveaux commits."""
        current_hash = self._get_latest_commit_hash()

        if current_hash and current_hash != self.last_commit_hash:
            pulses = self._get_git_pulses(limit=1)
            if pulses and self.on_pulse:
                # Envoyer le premier pulse (le plus récent)
                await self.on_pulse(pulses[0])
                print(f"🌊 Git Pulse: New commit detected - {pulses[0]['hash'][:8]}")

            self.last_commit_hash = current_hash

    def _get_latest_commit_hash(self) -> Optional[str]:
        """Récupère le hash du dernier commit."""
        try:
            result = self._run_git_command(["git", "rev-parse", "HEAD"], check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None

    def _get_git_pulses(
        self,
        limit: int = 50,
        since: Optional[str] = None,
        until: Optional[str] = None,
        author: Optional[str] = None,
        branch: Optional[str] = None,
        pulse_types: Optional[List[str]] = None,
        min_changes: Optional[int] = None,
        max_changes: Optional[int] = None,
        file_pattern: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Récupère et analyse les pulses Git avec des filtres avancés.
        """
        try:
            # Préparer les arguments de filtrage
            log_args = [
                "git", "log",
                f"-{limit}",
                "--pretty=format:%H|%an|%at|%s|%D",
            ]

            # Ajout des filtres
            if since:
                log_args.append(f"--since={since}")
            if until:
                log_args.append(f"--until={until}")
            if author:
                log_args.append(f"--author={author}")
            if branch:
                log_args.append(branch)
            if file_pattern:
                log_args.extend(["--", file_pattern])

            pulses = []
            # Exécuter la commande log avec les filtres
            log_result = self._run_git_command(log_args, check=True)
            log_lines = log_result.stdout.strip().split('\n')

            color_map = {
                'main': '#00ff9f',
                'master': '#00ff9f',
                'develop': '#00f0ff',
                'feature': '#a855f7',
                'fix': '#ff0055',
                'hotfix': '#ff0055',
                'default': '#22d3ee'
            }

            pulses = []
            for line in log_lines:
                try:
                    # Format: hash|author|timestamp|message|refs
                    parts = line.split('|')
                    if len(parts) < 4:
                        continue

                    hash_val, author, timestamp_str, message, refs = parts

                    # Filtrage par type de pulse
                    refs_lower = refs.lower()
                    pulse_type = 'commit'
                    if 'merge' in refs_lower:
                        pulse_type = 'merge'
                    elif any('origin/' in ref for ref in refs.split(', ')):
                        pulse_type = 'branch'

                    # Filtrage par type de pulse
                    if pulse_types and pulse_type not in pulse_types:
                        continue

                    # Récupérer les fichiers modifiés et statistiques
                    files_changed_result = self._run_git_command(
                        ["git", "show", "--name-status", "--pretty=", hash_val],
                        check=True
                    )

                    files_changed = [
                        line.split('\t')[1]
                        for line in files_changed_result.stdout.split('\n')
                        if line.strip() and '\t' in line
                    ]

                    # Calculer les insertions/suppressions
                    stats_result = self._run_git_command(
                        ["git", "show", "--shortstat", "--pretty=", hash_val],
                        check=True
                    )

                    stats_match = re.search(r'(\d+) insertions?\(\+\), (\d+) deletions?(-)', stats_result.stdout)
                    insertions = int(stats_match.group(1)) if stats_match else 0
                    deletions = int(stats_match.group(2)) if stats_match else 0

                    # Filtres sur les changements
                    total_changes = insertions + deletions
                    if min_changes is not None and total_changes < min_changes:
                        continue
                    if max_changes is not None and total_changes > max_changes:
                        continue

                    # Filtrer par pattern de fichier
                    if file_pattern and not any(file_pattern in file for file in files_changed):
                        continue

                    # Calculer l'intensité
                    intensity = min(1.0, total_changes / 500)  # Normaliser sur 500 changements max

                    # Choisir la couleur
                    color = color_map['default']
                    for keyword, col in color_map.items():
                        if keyword in refs_lower:
                            color = col
                            break

                    pulse_event = {
                        'id': hash_val[:8],
                        'type': pulse_type,
                        'hash': hash_val,
                        'author': author,
                        'message': message.strip(),
                        'timestamp': datetime.fromtimestamp(int(timestamp_str), tz=timezone.utc).isoformat(),
                        'insertions': insertions,
                        'deletions': deletions,
                        'filesChanged': files_changed,
                        'intensity': intensity,
                        'color': color
                    }

                    pulses.append(pulse_event)

                except Exception as e:
                    print(f"⚠ Erreur lors du traitement d'un commit : {e}")

            # Trier les pulses par timestamp (plus récent en premier)
            pulses.sort(key=lambda x: x['timestamp'], reverse=True)

            return pulses[:limit]

        except subprocess.CalledProcessError as e:
            print(f"⚠ Erreur Git : {e.stderr.strip() if e.stderr else 'unknown'}")
            return []
        except Exception as e:
            print(f"⚠ Erreur lors de la génération des pulses : {e}")
            return []

    def get_file_heat_map(self, days: int = 30) -> List[FileHeat]:
        """Calcule la heat map des fichiers modifiés."""
        try:
            # Obtenir l'historique des fichiers modifiés
            result = self._run_git_command(
                ["git", "log", f"--since={days} days ago", "--name-only", "--pretty=format:"],
                check=True
            )

            # Compter les modifications par fichier
            file_counts: Dict[str, int] = {}
            for line in result.stdout.strip().split('\n'):
                if line:
                    file_counts[line] = file_counts.get(line, 0) + 1

            # Obtenir la date de dernière modification
            heat_map = []
            max_count = max(file_counts.values()) if file_counts else 1

            for file_path, count in file_counts.items():
                # Obtenir la dernière date de modification
                try:
                    last_mod_result = self._run_git_command(
                        ["git", "log", "-1", "--format=%at", "--", file_path],
                        check=True
                    )

                    last_modified = datetime.fromtimestamp(
                        int(last_mod_result.stdout.strip()),
                        tz=timezone.utc
                    )
                except subprocess.CalledProcessError:
                    last_modified = datetime.now(timezone.utc)
                except Exception:
                    last_modified = datetime.now(timezone.utc)

                heat_map.append(FileHeat(
                    path=file_path,
                    modification_count=count,
                    last_modified=last_modified,
                    heat_level=count / max_count
                ))

            # Trier par heat level décroissant
            heat_map.sort(key=lambda x: x.heat_level, reverse=True)

            return heat_map[:20]  # Retourner les 20 fichiers les plus "chauds"

        except subprocess.CalledProcessError:
            return []

    def get_active_branches(self) -> List[BranchActivity]:
        """Liste les branches avec leur activité."""
        try:
            # Obtenir toutes les branches
            branches_result = self._run_git_command(
                ["git", "branch", "-a"],
                check=True
            )

            branches = []
            current_branch = None

            for line in branches_result.stdout.strip().split('\n'):
                if line.startswith('*'):
                    current_branch = line[2:].strip()
                    branch_name = current_branch
                else:
                    branch_name = line.strip()

                if not branch_name or branch_name.startswith('remotes/'):
                    continue

                # Obtenir le dernier commit de la branche
                try:
                    last_commit_result = self._run_git_command(
                        ["git", "log", "-1", "--format=%at", branch_name],
                        check=True
                    )

                    last_commit = datetime.fromtimestamp(
                        int(last_commit_result.stdout.strip()),
                        tz=timezone.utc
                    )

                    # Compter les commits ahead de main/master
                    commits_ahead = 0
                    try:
                        ahead_result = self._run_git_command(
                            ["git", "rev-list", "--count", f"main..{branch_name}"],
                            check=False
                        )
                        commits_ahead = int(ahead_result.stdout.strip()) if ahead_result.returncode == 0 else 0
                    except Exception as e:
                        print(f"⚠ Error getting commits ahead for {branch_name}: {e}")
                        pass

                    # Assigner une couleur selon le nom de la branche
                    color_map = {
                        'main': '#00ff9f',
                        'master': '#00ff9f',
                        'develop': '#00f0ff',
                        'feature': '#a855f7',
                        'fix': '#ff0055',
                        'hotfix': '#ff0055',
                    }

                    color = '#22d3ee'  # Default cyan
                    for keyword, col in color_map.items():
                        if keyword in branch_name.lower():
                            color = col
                            break

                    branches.append(BranchActivity(
                        name=branch_name,
                        is_active=(branch_name == current_branch),
                        last_commit=last_commit,
                        commits_ahead=commits_ahead,
                        color=color
                    ))

                except subprocess.CalledProcessError:
                    pass

            return branches

        except subprocess.CalledProcessError:
            return []