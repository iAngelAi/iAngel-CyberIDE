"""
Tests unitaires pour le moteur Git Pulse

Ce module teste les différentes fonctionnalités de filtrage
du moteur Git Pulse.
"""

import pytest
import os
import subprocess
from datetime import datetime, timedelta
from neural_cli.git_pulse import GitPulseEngine

@pytest.fixture
def temp_git_repo(tmp_path):
    """
    Crée un dépôt Git temporaire avec des commits de test.
    """
    # Créer un dépôt Git temporaire
    subprocess.run(["git", "init"], cwd=tmp_path, check=True)

    # Configurer un utilisateur Git
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=tmp_path,
        check=True
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=tmp_path,
        check=True
    )

    # Créer quelques fichiers et commits
    commits_data = [
        {"file": "README.md", "content": "# Project v1", "message": "Initial commit"},
        {"file": "src/main.py", "content": "print('Hello')", "message": "Add main script"},
        {"file": "src/utils.py", "content": "def helper():\n    pass", "message": "Add utility functions"},
        {"file": "tests/test_main.py", "content": "def test_main():\n    assert True", "message": "Add first test"},
        {"file": "docs/README.md", "content": "# Documentation", "message": "Add documentation"},
    ]

    for commit in commits_data:
        # Créer ou modifier le fichier
        file_path = tmp_path / commit['file']
        os.makedirs(file_path.parent, exist_ok=True)
        file_path.write_text(commit['content'])

        # Ajouter et commiter
        subprocess.run(["git", "add", commit['file']], cwd=tmp_path, check=True)
        subprocess.run(
            ["git", "commit", "-m", commit['message']],
            cwd=tmp_path,
            check=True
        )

    return tmp_path

class TestGitPulseFilters:
    """
    Tests des filtres avancés pour les pulses Git.
    """

    def test_default_pulse_retrieval(self, temp_git_repo):
        """
        Test la récupération des pulses sans filtres.
        """
        pulse_engine = GitPulseEngine(str(temp_git_repo))
        pulses = pulse_engine._get_git_pulses()

        assert len(pulses) > 0
        assert len(pulses) <= 50  # Limite par défaut

        # Vérifier la structure des pulses
        required_keys = [
            'id', 'type', 'hash', 'author', 'message',
            'timestamp', 'insertions', 'deletions',
            'filesChanged', 'intensity', 'color'
        ]
        for pulse in pulses:
            for key in required_keys:
                assert key in pulse

    def test_limit_filter(self, temp_git_repo):
        """
        Test le filtre de limite.
        """
        pulse_engine = GitPulseEngine(str(temp_git_repo))
        pulses = pulse_engine._get_git_pulses(limit=2)

        assert len(pulses) == 2

    def test_pulse_type_filter(self, temp_git_repo):
        """
        Test le filtrage par type de pulse.
        """
        # Note: Comme nos commits sont tous des commits standard
        pulse_engine = GitPulseEngine(str(temp_git_repo))
        pulses = pulse_engine._get_git_pulses(pulse_types=['commit'])

        assert len(pulses) > 0
        assert all(pulse['type'] == 'commit' for pulse in pulses)

    def test_file_pattern_filter(self, temp_git_repo):
        """
        Test le filtrage par pattern de fichier.
        """
        pulse_engine = GitPulseEngine(str(temp_git_repo))

        # Filtrer les pulses touchant le dossier src/
        pulses = pulse_engine._get_git_pulses(file_pattern='src/')

        assert len(pulses) > 0
        assert all(any('src/' in file for file in pulse['filesChanged']) for pulse in pulses)

    def test_multiple_filters_combined(self, temp_git_repo):
        """
        Test de combinaison de plusieurs filtres.
        """
        pulse_engine = GitPulseEngine(str(temp_git_repo))

        pulses = pulse_engine._get_git_pulses(
            limit=1,
            pulse_types=['commit'],
            file_pattern='src/'
        )

        assert len(pulses) == 1
        assert pulses[0]['type'] == 'commit'
        assert any('src/' in file for file in pulses[0]['filesChanged'])

    def test_error_handling(self, tmp_path):
        """
        Test de la gestion des erreurs avec un répertoire non-Git.
        """
        pulse_engine = GitPulseEngine(str(tmp_path))

        # Un répertoire non-Git doit retourner une liste vide sans lever d'exception
        pulses = pulse_engine._get_git_pulses()
        assert len(pulses) == 0

    def test_intensity_calculation(self, temp_git_repo):
        """
        Test du calcul de l'intensité des pulses.
        """
        pulse_engine = GitPulseEngine(str(temp_git_repo))
        pulses = pulse_engine._get_git_pulses()

        for pulse in pulses:
            # L'intensité doit être entre 0 et 1
            assert 0 <= pulse['intensity'] <= 1

            # Vérifier que l'intensité reflète le nombre de changements
            total_changes = pulse['insertions'] + pulse['deletions']
            expected_intensity = min(1.0, total_changes / 500)
            assert abs(pulse['intensity'] - expected_intensity) < 1e-6

    def test_large_repo_complex_filters(self, temp_git_repo):
        """
        Test de filtres complexes sur un dépôt plus grand.
        Créer des commits variés pour tester des scénarios avancés.
        """
        # Ajouter des commits supplémentaires variés
        additional_commits = [
            {"file": "src/complex/module1.py", "content": "class ComplexModule1:\n    def method1(self):\n        pass", "message": "Add complex module 1", "author": "dev1"},
            {"file": "src/complex/module2.py", "content": "class ComplexModule2:\n    def method2(self):\n        pass", "message": "Add complex module 2", "author": "dev2"},
            {"file": "tests/test_complex.py", "content": "def test_complex_modules():\n    assert True", "message": "Add complex tests", "author": "dev1"},
            {"file": "docs/advanced.md", "content": "# Advanced Documentation", "message": "Update advanced docs", "author": "dev3"}
        ]

        for commit in additional_commits:
            file_path = temp_git_repo / commit['file']
            os.makedirs(file_path.parent, exist_ok=True)
            file_path.write_text(commit['content'])

            # Configurer l'auteur pour ce commit
            subprocess.run(
                ["git", "config", "user.name", commit['author']],
                cwd=temp_git_repo,
                check=True
            )

            subprocess.run(["git", "add", commit['file']], cwd=temp_git_repo, check=True)
            subprocess.run(
                ["git", "commit", "-m", commit['message']],
                cwd=temp_git_repo,
                check=True
            )

        pulse_engine = GitPulseEngine(str(temp_git_repo))

        # Test 1: Filtres multiples complexes
        complex_pulses = pulse_engine._get_git_pulses(
            limit=3,
            author='dev1',
            file_pattern='src/complex',
            pulse_types=['commit']
        )

        assert len(complex_pulses) > 0
        assert all(pulse['author'] == 'dev1' for pulse in complex_pulses)
        assert all(any('src/complex' in file for file in pulse['filesChanged']) for pulse in complex_pulses)
        assert all(pulse['type'] == 'commit' for pulse in complex_pulses)

        # Test 2: Filtres avec changements minimaux
        change_filtered_pulses = pulse_engine._get_git_pulses(
            min_changes=10,
            max_changes=100
        )

        assert len(change_filtered_pulses) > 0
        assert all(
            10 <= (pulse['insertions'] + pulse['deletions']) <= 100
            for pulse in change_filtered_pulses
        )

        # Test 3: Vérification de la cohérence des métadonnées
        for pulse in complex_pulses:
            assert len(pulse['id']) == 8
            assert pulse['hash']  # Hash complet doit être présent
            assert pulse['timestamp']  # Horodatage doit être présent
            assert pulse['filesChanged']  # Liste de fichiers non vide

    def test_edge_cases_and_boundary_conditions(self, temp_git_repo):
        """
        Test des cas limites et conditions aux frontières.
        """
        pulse_engine = GitPulseEngine(str(temp_git_repo))

        # Test 1: Limite zéro
        zero_limit_pulses = pulse_engine._get_git_pulses(limit=0)
        assert len(zero_limit_pulses) == 0

        # Test 2: Filtres impossibles
        impossible_filtered_pulses = pulse_engine._get_git_pulses(
            author='NonexistentUser',
            file_pattern='non/existent/path'
        )
        assert len(impossible_filtered_pulses) == 0

        # Test 3: Paramètres de changements incohérents
        inconsistent_change_pulses = pulse_engine._get_git_pulses(
            min_changes=200,
            max_changes=100
        )
        assert len(inconsistent_change_pulses) == 0

        # Test 4: Types de pulse invalides
        invalid_type_pulses = pulse_engine._get_git_pulses(
            pulse_types=['invalid_type']
        )
        assert len(invalid_type_pulses) == 0

    def test_time_based_filtering(self, temp_git_repo):
        """
        Test des filtres basés sur le temps.
        """
        # Attendre un peu pour créer des différences de timestamp
        import time
        time.sleep(1)

        pulse_engine = GitPulseEngine(str(temp_git_repo))

        # Test 1: Depuis un temps récent
        recent_pulses = pulse_engine._get_git_pulses(
            since='1 minute ago'
        )
        assert len(recent_pulses) > 0

        # Test 2: Période spécifique
        current_time = datetime.now()
        one_hour_ago = (current_time - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
        period_pulses = pulse_engine._get_git_pulses(
            since=one_hour_ago,
            until=current_time.strftime('%Y-%m-%d %H:%M:%S')
        )
        assert len(period_pulses) > 0

    def test_sorting_and_order(self, temp_git_repo):
        """
        Test de l'ordre et du tri des pulses.
        """
        pulse_engine = GitPulseEngine(str(temp_git_repo))

        # Récupérer tous les pulses triés
        all_pulses = pulse_engine._get_git_pulses()

        # Vérifier que les pulses sont triés du plus récent au plus ancien
        assert len(all_pulses) > 1
        for i in range(1, len(all_pulses)):
            assert datetime.fromisoformat(all_pulses[i-1]['timestamp']) >= datetime.fromisoformat(all_pulses[i]['timestamp'])