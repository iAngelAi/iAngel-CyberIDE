import asyncio
import json
import socket
import time
import functools
import inspect
from typing import Optional, Any
from dataclasses import dataclass, asdict

# Configuration par défaut
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8123  # Port UDP dédié au Neural Core

@dataclass
class SynapseActivation:
    """Représente l'activation d'une synapse (fonction/méthode)"""
    timestamp: float
    file_path: str
    function_name: str
    region: str
    layer: str
    status: str  # 'active', 'success', 'error'
    duration_ms: float = 0.0
    error_message: Optional[str] = None
    metadata: Optional[dict] = None

class NeuralTransmitter:
    """
    Client UDP ultra-léger pour envoyer les signaux neuronaux.
    Utilise un socket UDP non-bloquant pour éviter d'impacter les perfs de l'app hôte.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NeuralTransmitter, cls).__new__(cls)
            cls._instance._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            cls._instance._sock.setblocking(False)
        return cls._instance

    def send_pulse(self, activation: SynapseActivation):
        try:
            payload = json.dumps(asdict(activation)).encode('utf-8')
            # Fire and forget
            self._sock.sendto(payload, (DEFAULT_HOST, DEFAULT_PORT))
        except Exception:
            # Le système nerveux ne doit jamais tuer l'hôte
            pass

def neural_synapse(region: str = "cortex", layer: str = "logic", metadata: dict = None):
    """
    Décorateur pour connecter une fonction au Neural Core.
    
    Usage:
        @neural_synapse(region="auth", layer="security")
        def login_user(creds):
            ...
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            transmitter = NeuralTransmitter()
            start_time = time.time()
            file_path = inspect.getfile(func)
            func_name = func.__name__
            
            # 1. Signal d'activation (Firing)
            activation = SynapseActivation(
                timestamp=start_time,
                file_path=file_path,
                function_name=func_name,
                region=region,
                layer=layer,
                status="active",
                metadata=metadata
            )
            transmitter.send_pulse(activation)

            try:
                # Exécution de la fonction réelle
                result = func(*args, **kwargs)
                
                # 2. Signal de succès (Resting state)
                duration = (time.time() - start_time) * 1000
                success_pulse = SynapseActivation(
                    timestamp=time.time(),
                    file_path=file_path,
                    function_name=func_name,
                    region=region,
                    layer=layer,
                    status="success",
                    duration_ms=duration,
                    metadata=metadata
                )
                transmitter.send_pulse(success_pulse)
                return result

            except Exception as e:
                # 3. Signal de douleur (Error)
                duration = (time.time() - start_time) * 1000
                error_pulse = SynapseActivation(
                    timestamp=time.time(),
                    file_path=file_path,
                    function_name=func_name,
                    region=region,
                    layer=layer,
                    status="error",
                    duration_ms=duration,
                    error_message=str(e),
                    metadata=metadata
                )
                transmitter.send_pulse(error_pulse)
                raise e

        return wrapper
    return decorator

# Fonction helper pour les blocs de code sans décorateur
class NeuralContext:
    """
    Context manager pour tracer des blocs de code.
    with NeuralContext("database", "query"):
        db.execute(...)
    """
    def __init__(self, region: str, layer: str = "logic"):
        self.region = region
        self.layer = layer
        self.transmitter = NeuralTransmitter()
        self.start_time = 0
        
        # Récupération de l'appelant
        frame = inspect.stack()[1]
        self.file_path = frame.filename
        self.func_name = frame.function

    def __enter__(self):
        self.start_time = time.time()
        self.transmitter.send_pulse(SynapseActivation(
            timestamp=self.start_time,
            file_path=self.file_path,
            function_name=self.func_name,
            region=self.region,
            layer=self.layer,
            status="active"
        ))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (time.time() - self.start_time) * 1000
        status = "error" if exc_type else "success"
        error_msg = str(exc_val) if exc_val else None
        
        self.transmitter.send_pulse(SynapseActivation(
            timestamp=time.time(),
            file_path=self.file_path,
            function_name=self.func_name,
            region=self.region,
            layer=self.layer,
            status=status,
            duration_ms=duration,
            error_message=error_msg
        ))
