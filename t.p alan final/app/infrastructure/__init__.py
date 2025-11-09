"""
Módulo de Infraestructura
Contiene componentes de bajo nivel como sockets, TCP, servicios distribuidos y serialización
"""

# Evitar importar módulos que se ejecutan como scripts para prevenir warnings de Python
# Estos módulos se importan solo cuando se necesitan (lazy imports)

# Importar solo módulos que no se ejecutan directamente como scripts
from app.infrastructure.tcp_client import save_score_via_tcp
from app.infrastructure.serialization import Serializer, serialize, deserialize

# distributed_service y tcp_server se ejecutan como scripts, así que no los importamos aquí
# para evitar el warning: "found in sys.modules after import of package"
# Se pueden importar directamente cuando se necesiten:
#   from app.infrastructure.tcp_server import start_server
#   from app.infrastructure.distributed_service import DistributedService, DistributedServiceClient

__all__ = [
    'save_score_via_tcp',
    'Serializer',
    'serialize',
    'deserialize'
]

