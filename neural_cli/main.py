"""
CyberIDE Neural Core - FastAPI Backend

This is the main entry point for the Neural Core backend.
It provides WebSocket communication, file watching, and real-time
project health monitoring for the 3D brain visualization.
"""

import asyncio
import json
import os
import random
from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .models import (
    NeuralStatus,
    FileChangeEvent,
    TestResult,
    WebSocketMessage,
    BrainRegion
)
from .file_watcher import FileWatcher
from .test_analyzer import TestAnalyzer
from .metric_calculator import MetricCalculator
from .file_mapper import FileMapper, FileMappingResult
from .git_pulse import GitPulseEngine


# Global state
class NeuralCore:
    """Global state for the Neural Core system."""
    def __init__(self):
        self.project_root: Path = Path.cwd()
        self.watcher: FileWatcher | None = None
        self.test_analyzer: TestAnalyzer | None = None
        self.metric_calculator: MetricCalculator | None = None
        self.file_mapper: FileMapper | None = None
        self.git_pulse: GitPulseEngine | None = None
        self.current_file_mapping: FileMappingResult | None = None
        self.current_status: NeuralStatus | None = None
        self.connected_clients: Set[WebSocket] = set()
        self.status_file: Path = self.project_root / "neural_status.json"
        self.test_running: bool = False

    async def broadcast(self, message: WebSocketMessage):
        """Broadcast a message to all connected WebSocket clients."""
        disconnected = set()

        for client in self.connected_clients:
            try:
                await client.send_json(message.model_dump(mode='json'))
            except Exception as e:
                print(f"⚠ Error sending to client: {e}")
                disconnected.add(client)

        # Remove disconnected clients
        self.connected_clients -= disconnected

    def save_status(self):
        """Save current neural status to neural_status.json."""
        if self.current_status is None:
            return

        try:
            with open(self.status_file, 'w') as f:
                json.dump(
                    self.current_status.model_dump(mode='json'),
                    f,
                    indent=2
                )
        except Exception as e:
            print(f"❌ Failed to save status: {e}")

    def load_status(self) -> NeuralStatus:
        """Load neural status from file, or create new."""
        if self.status_file.exists():
            try:
                with open(self.status_file, 'r') as f:
                    data = json.load(f)
                    # Convert region dicts back to BrainRegion objects
                    if 'regions' in data:
                        regions = {}
                        for name, region_data in data['regions'].items():
                            regions[name] = BrainRegion(**region_data)
                        data['regions'] = regions
                    return NeuralStatus(**data)
            except Exception as e:
                print(f"⚠ Failed to load status: {e}")

        # Return default status
        return NeuralStatus()


# Create global neural core
neural_core = NeuralCore()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    # Startup
    print("\n" + "=" * 60)
    print("🧠 CyberIDE NEURAL CORE Initializing...")
    print("=" * 60)

    # Set project root (can be overridden via env var)
    project_root_env = os.getenv("CYBER_PROJECT_ROOT")
    if project_root_env:
        neural_core.project_root = Path(project_root_env)
    print(f"ℹ Project Root: {neural_core.project_root}")

    # Initialize components
    neural_core.test_analyzer = TestAnalyzer(str(neural_core.project_root))
    neural_core.metric_calculator = MetricCalculator(str(neural_core.project_root))
    neural_core.file_mapper = FileMapper(str(neural_core.project_root))

    # Load or create initial status
    neural_core.current_status = neural_core.load_status()
    print(f"✓ Loaded neural status (illumination: {neural_core.current_status.illumination:.1%})")

    # Perform initial file mapping
    print("\nℹ Mapping source files to test files...")
    neural_core.current_file_mapping = neural_core.file_mapper.scan_and_map()
    stats = neural_core.file_mapper.get_mapping_stats(neural_core.current_file_mapping)
    print(f"✓ File mapping complete:")
    print(f"  - Source files: {stats['total_source_files']}")
    print(f"  - Test files: {stats['total_test_files']}")
    print(f"  - Coverage: {stats['coverage_percentage']:.1f}%")
    print(f"  - Connections: {stats['strong_connections']} strong, {stats['weak_connections']} weak")

    # Perform initial scan
    print("\nℹ Performing initial project scan...")
    await perform_initial_scan()

    # Start file watcher
    neural_core.watcher = FileWatcher(
        project_root=str(neural_core.project_root),
        on_change_callback=handle_file_change
    )
    neural_core.watcher.start()

    # Start Git Pulse Engine
    print("\nℹ Starting Git Pulse Engine...")
    neural_core.git_pulse = GitPulseEngine(str(neural_core.project_root))

    # Configure Git Pulse callbacks
    async def handle_git_pulse(pulse_data: dict):
        """Handle Git pulse events."""
        await neural_core.broadcast(
            WebSocketMessage(
                type="git_pulse",
                data=pulse_data
            )
        )

    neural_core.git_pulse.on_pulse = handle_git_pulse

    # Start Git Pulse in background
    asyncio.create_task(neural_core.git_pulse.start())
    print("✓ Git Pulse Engine started")

    print("\n" + "=" * 60)
    print("✓ NEURAL CORE Online - Ready to illuminate")
    print("=" * 60)
    print(f"WebSocket endpoint: ws://localhost:8000/ws")
    print(f"Status file: {neural_core.status_file}")
    print("=" * 60 + "\n")

    yield

    # Shutdown
    print("\n🧠 Neural Core shutting down...")
    if neural_core.watcher:
        neural_core.watcher.stop()
    if neural_core.git_pulse:
        neural_core.git_pulse.stop()

    # Save final status
    neural_core.save_status()
    print("✓ Neural Core offline\n")


# Create FastAPI app
app = FastAPI(
    title="CyberIDE Neural Core",
    description="Backend API for CyberIDE brain visualization and project monitoring",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# WebSocket Endpoint
# ============================================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Main WebSocket endpoint for real-time communication.

    Clients connect here to receive live updates about project health,
    test results, and file changes.
    """
    await websocket.accept()
    neural_core.connected_clients.add(websocket)

    client_id = id(websocket)
    print(f"✓ Client connected [ID: {client_id}]")
    print(f"  Total clients: {len(neural_core.connected_clients)}")

    try:
        # Send current status immediately
        if neural_core.current_status:
            await websocket.send_json(
                WebSocketMessage(
                    type="neural_status",
                    data=neural_core.current_status.model_dump(mode='json')
                ).model_dump(mode='json')
            )

        # Send current file mapping
        if neural_core.current_file_mapping:
            await websocket.send_json(
                WebSocketMessage(
                    type="file_mapping",
                    data={
                        "source_files": neural_core.current_file_mapping.source_files,
                        "test_files": neural_core.current_file_mapping.test_files,
                        "connections": neural_core.current_file_mapping.connections
                    }
                ).model_dump(mode='json')
            )

        # Keep connection alive and handle messages
        while True:
            try:
                # Receive messages from client (for future interactivity)
                data = await websocket.receive_json()
                command = data.get("command")

                if command == "run_tests":
                    # Client requested test run
                    await run_tests_and_update()
                elif command == "refresh_status":
                    # Client requested status refresh
                    await websocket.send_json(
                        WebSocketMessage(
                            type="neural_status",
                            data=neural_core.current_status.model_dump(mode='json')
                        ).model_dump(mode='json')
                    )
            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"⚠ WebSocket error: {e}")
                break

    finally:
        neural_core.connected_clients.discard(websocket)
        print(f"✓ Client disconnected [ID: {client_id}]")
        print(f"  Total clients: {len(neural_core.connected_clients)}")


# ============================================================================
# REST API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "service": "CyberIDE Neural Core",
        "status": "online",
        "version": "1.0.0",
        "illumination": neural_core.current_status.illumination if neural_core.current_status else 0.0,
        "connected_clients": len(neural_core.connected_clients)
    }


@app.get("/status", response_model=NeuralStatus)
async def get_status():
    """Get current neural status."""
    if neural_core.current_status is None:
        raise HTTPException(status_code=503, detail="Neural status not available")
    return neural_core.current_status


@app.post("/tests/run")
async def run_tests():
    """Trigger a test run manually."""
    if neural_core.test_running:
        return JSONResponse(
            status_code=409,
            content={"message": "Tests already running"}
        )

    # Run tests in background
    asyncio.create_task(run_tests_and_update())

    return {"message": "Test run initiated"}


@app.get("/tests/results")
async def get_test_results():
    """Get latest test results."""
    # This will be enhanced to return detailed test history
    if neural_core.current_status:
        return {
            "regions": neural_core.current_status.regions,
            "diagnostics": neural_core.current_status.diagnostics
        }
    return {"message": "No test results available"}


@app.get("/watcher/status")
async def get_watcher_status():
    """Get file watcher status and stats."""
    if neural_core.watcher:
        return neural_core.watcher.get_stats()
    return {"error": "File watcher not initialized"}


@app.get("/metrics")
async def get_metrics():
    """Get detailed project metrics."""
    if not neural_core.metric_calculator:
        raise HTTPException(status_code=503, detail="Metric calculator not available")

    file_counts = neural_core.metric_calculator.count_files_by_region()

    return {
        "file_counts": file_counts,
        "illumination": neural_core.current_status.illumination if neural_core.current_status else 0.0,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/files/mapping")
async def get_file_mapping():
    """Get the current file mapping between source and test files."""
    if not neural_core.file_mapper or not neural_core.current_file_mapping:
        raise HTTPException(status_code=503, detail="File mapping not available")

    # Convert dataclass to dict for JSON serialization
    mapping_data = {
        "source_files": neural_core.current_file_mapping.source_files,
        "test_files": neural_core.current_file_mapping.test_files,
        "connections": neural_core.current_file_mapping.connections,
        "unmapped_sources": neural_core.current_file_mapping.unmapped_sources,
        "unmapped_tests": neural_core.current_file_mapping.unmapped_tests,
        "stats": neural_core.file_mapper.get_mapping_stats(neural_core.current_file_mapping)
    }

    return mapping_data


@app.post("/files/refresh_mapping")
async def refresh_file_mapping():
    """Refresh the file mapping by rescanning the project."""
    if not neural_core.file_mapper:
        raise HTTPException(status_code=503, detail="File mapper not available")

    # Rescan the project
    neural_core.current_file_mapping = neural_core.file_mapper.scan_and_map()

    # Broadcast the new mapping to connected clients
    await neural_core.broadcast(
        WebSocketMessage(
            type="file_mapping",
            data={
                "source_files": neural_core.current_file_mapping.source_files,
                "test_files": neural_core.current_file_mapping.test_files,
                "connections": neural_core.current_file_mapping.connections
            }
        )
    )

    stats = neural_core.file_mapper.get_mapping_stats(neural_core.current_file_mapping)
    return {"message": "File mapping refreshed", "stats": stats}


@app.get("/git/dashboard")
async def get_git_dashboard():
    """Get comprehensive Git dashboard data."""
    if not neural_core.git_pulse:
        raise HTTPException(status_code=503, detail="Git Pulse Engine not available")

    # Obtenir les différentes statistiques Git
    heat_map = neural_core.git_pulse.get_file_heat_map(days=30)
    branches = neural_core.git_pulse.get_active_branches()

    # Calcul des commits récents (simulé pour l'instant)
    recent_commits = [
        {
            "hash": "abc123",
            "author": "Fil LeFebvre",
            "message": "Impl\u00e9mentation du dashboard Git",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "insertions": 150,
            "deletions": 50,
            "filesChanged": ["src/components/GitDashboard/GitDashboard.tsx"]
        },
        # Ajouter d'autres commits récents simulés
    ]

    # Calcul des statistiques des auteurs
    total_commits = len(recent_commits)
    authors_stats = {}
    for commit in recent_commits:
        authors_stats[commit['author']] = authors_stats.get(commit['author'], 0) + 1

    active_authors = [
        {
            "name": author,
            "commitCount": count,
            "percentageOfTotal": (count / total_commits) * 100
        }
        for author, count in authors_stats.items()
    ]

    # Si aucun dépôt Git n'est détecté, utiliser des données simulées
    try:
        # Tenter de créer une instance GitPulseEngine
        pulse_engine = GitPulseEngine(str(neural_core.project_root))
        pulses = pulse_engine._get_git_pulses(
            limit=10,
            since='1 month ago',  # Filtrer les commits du dernier mois
            pulse_types=['commit', 'merge', 'branch'],
            min_changes=10,  # Au moins 10 changements
            max_changes=500  # Moins de 500 changements
        )
    except Exception:
        # Données simulées de secours
        pulses = [
            {
                "id": f"pulse_{i}",
                "type": pulse_type,
                "hash": f"commit_hash_{i}",
                "author": "Fil LeFebvre",
                "message": f"Message de {pulse_type.capitalize()} {i}",
                "timestamp": (datetime.now(timezone.utc) - timedelta(days=i)).isoformat(),
                "insertions": random.randint(10, 200),
                "deletions": random.randint(5, 100),
                "filesChanged": [
                    f"src/components/GitDashboard/pulse_{i}.{ext}"
                    for ext in ['tsx', 'ts', 'py']
                ],
                "intensity": random.random(),
                "color": {
                    'commit': '#22d3ee',   # Cyan
                    'merge': '#a855f7',    # Violet
                    'branch': '#10b981'    # Vert émeraude
                }[pulse_type]
            }
            for i, pulse_type in enumerate(
                random.choices(['commit', 'merge', 'branch'], k=10)
            )
        ]

    return {
        "branches": [
            {
                "name": b.name,
                "isActive": b.is_active,
                "lastCommit": b.last_commit.isoformat(),
                "commitsAhead": b.commits_ahead,
                "color": b.color
            }
            for b in branches
        ],
        "heatMap": [
            {
                "path": f.path,
                "modificationCount": f.modification_count,
                "lastModified": f.last_modified.isoformat(),
                "heatLevel": f.heat_level
            }
            for f in heat_map
        ],
        "recentCommits": recent_commits,
        "pulses": pulses,
        "totalCommits": total_commits,
        "activeAuthors": active_authors,
        "repositoryStats": {
            "totalFiles": neural_core.file_mapper.scan_and_map().total_files if neural_core.file_mapper else 0,
            "linesOfCode": sum(
                file['linesOfCode']
                for file in neural_core.file_mapper.scan_and_map().source_files
            ) if neural_core.file_mapper else 0,
            "lastUpdated": datetime.now(timezone.utc).isoformat()
        }
    }


# ============================================================================
# Event Handlers
# ============================================================================

def handle_file_change(event: FileChangeEvent):
    """
    Handle file system change events.

    This is called by the file watcher when files change.
    """
    print(f"ℹ File {event.event_type}: {Path(event.file_path).name}")

    # Broadcast file change to clients
    asyncio.create_task(
        neural_core.broadcast(
            WebSocketMessage(
                type="file_change",
                data=event.model_dump(mode='json')
            )
        )
    )

    # Should we run tests?
    if neural_core.test_analyzer and neural_core.test_analyzer.should_run_tests(event.file_path):
        print("  → Triggering test run...")
        asyncio.create_task(run_tests_and_update())


async def run_tests_and_update():
    """Run tests and update neural status."""
    if neural_core.test_running:
        print("⚠ Tests already running, skipping...")
        return

    neural_core.test_running = True

    try:
        print("\n" + "=" * 50)
        print("🧪 Running tests...")
        print("=" * 50)

        # Run tests
        test_result = neural_core.test_analyzer.run_tests()

        # Print summary
        print(neural_core.test_analyzer.format_test_summary(test_result))

        # Update metrics
        await update_neural_status(test_result)

        # Broadcast test results
        await neural_core.broadcast(
            WebSocketMessage(
                type="test_result",
                data=test_result.model_dump(mode='json')
            )
        )

    except Exception as e:
        print(f"❌ Error running tests: {e}")
    finally:
        neural_core.test_running = False


async def update_neural_status(test_result: TestResult = None):
    """Update the neural status based on current project state."""
    if not neural_core.metric_calculator:
        return

    # Get file counts
    file_counts = neural_core.metric_calculator.count_files_by_region()

    # Calculate new status
    test_data = {
        "passed": test_result.passed if test_result else 0,
        "failed": test_result.failed if test_result else 0,
        "total": test_result.total_tests if test_result else 0
    }

    coverage = test_result.coverage_percentage if test_result else 0.0

    neural_core.current_status = neural_core.metric_calculator.calculate_neural_status(
        test_coverage=coverage,
        test_results=test_data,
        file_counts=file_counts
    )

    # Save to file
    neural_core.save_status()

    # Broadcast updated status
    await neural_core.broadcast(
        WebSocketMessage(
            type="neural_status",
            data=neural_core.current_status.model_dump(mode='json')
        )
    )

    print(f"✓ Neural status updated (illumination: {neural_core.current_status.illumination:.1%})")


async def perform_initial_scan():
    """Perform initial project scan on startup."""
    # Check if tests exist
    if neural_core.test_analyzer:
        test_files = neural_core.test_analyzer.get_test_files()
        if len(test_files) == 0:
            print("⚠ No test files found - creating placeholder tests...")
            neural_core.test_analyzer.create_placeholder_tests()
        else:
            print(f"✓ Found {len(test_files)} test file(s)")

    # Run initial test scan
    await run_tests_and_update()


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point for running the server."""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║             🧠 CyberIDE NEURAL CORE 🧠                    ║
    ║                                                           ║
    ║         Neural Architecture for IDE Illumination         ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    # Run server
    uvicorn.run(
        "neural_cli.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload (we have our own file watcher)
        log_level="info"
    )


if __name__ == "__main__":
    main()
