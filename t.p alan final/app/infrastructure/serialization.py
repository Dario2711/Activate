"""
Módulo de Serialización Mejorado
Proporciona funciones para serializar/deserializar datos usando JSON y Pickle
"""
import json
import pickle
import base64
from typing import Any, Dict, Optional


class Serializer:
    """Clase para manejar serialización de datos"""
    
    @staticmethod
    def serialize_json(data: Any) -> str:
        """Serializa datos a JSON string"""
        try:
            return json.dumps(data, default=str, ensure_ascii=False)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Error serializando a JSON: {e}")
    
    @staticmethod
    def deserialize_json(data: str) -> Any:
        """Deserializa datos desde JSON string"""
        try:
            return json.loads(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error deserializando JSON: {e}")
    
    @staticmethod
    def serialize_pickle(data: Any) -> bytes:
        """Serializa datos a bytes usando Pickle"""
        try:
            return pickle.dumps(data)
        except pickle.PicklingError as e:
            raise ValueError(f"Error serializando con Pickle: {e}")
    
    @staticmethod
    def deserialize_pickle(data: bytes) -> Any:
        """Deserializa datos desde bytes usando Pickle"""
        try:
            return pickle.loads(data)
        except pickle.UnpicklingError as e:
            raise ValueError(f"Error deserializando con Pickle: {e}")
    
    @staticmethod
    def serialize_pickle_base64(data: Any) -> str:
        """Serializa datos a string base64 usando Pickle (útil para JSON)"""
        try:
            pickled = pickle.dumps(data)
            return base64.b64encode(pickled).decode('utf-8')
        except Exception as e:
            raise ValueError(f"Error serializando con Pickle+Base64: {e}")
    
    @staticmethod
    def deserialize_pickle_base64(data: str) -> Any:
        """Deserializa datos desde string base64 usando Pickle"""
        try:
            pickled = base64.b64decode(data.encode('utf-8'))
            return pickle.loads(pickled)
        except Exception as e:
            raise ValueError(f"Error deserializando con Pickle+Base64: {e}")
    
    @staticmethod
    def serialize_hybrid(data: Any, use_pickle: bool = False) -> Dict[str, Any]:
        """
        Serialización híbrida: JSON para datos simples, Pickle+Base64 para objetos complejos
        """
        try:
            # Intentar JSON primero
            if not use_pickle:
                json_str = json.dumps(data, default=str, ensure_ascii=False)
                return {
                    'format': 'json',
                    'data': json_str
                }
        except (TypeError, ValueError):
            # Si JSON falla, usar Pickle
            pass
        
        # Usar Pickle para objetos complejos
        try:
            pickled_b64 = Serializer.serialize_pickle_base64(data)
            return {
                'format': 'pickle',
                'data': pickled_b64
            }
        except Exception as e:
            raise ValueError(f"Error en serialización híbrida: {e}")
    
    @staticmethod
    def deserialize_hybrid(serialized: Dict[str, Any]) -> Any:
        """Deserializa datos desde formato híbrido"""
        format_type = serialized.get('format')
        data = serialized.get('data')
        
        if format_type == 'json':
            return Serializer.deserialize_json(data)
        elif format_type == 'pickle':
            return Serializer.deserialize_pickle_base64(data)
        else:
            raise ValueError(f"Formato de serialización desconocido: {format_type}")


# Funciones de utilidad para uso directo
def serialize(data: Any, method: str = 'json') -> Any:
    """
    Serializa datos usando el método especificado
    
    Args:
        data: Datos a serializar
        method: 'json', 'pickle', 'pickle_base64', o 'hybrid'
    
    Returns:
        Datos serializados según el método
    """
    if method == 'json':
        return Serializer.serialize_json(data)
    elif method == 'pickle':
        return Serializer.serialize_pickle(data)
    elif method == 'pickle_base64':
        return Serializer.serialize_pickle_base64(data)
    elif method == 'hybrid':
        return Serializer.serialize_hybrid(data)
    else:
        raise ValueError(f"Método de serialización desconocido: {method}")


def deserialize(data: Any, method: str = 'json') -> Any:
    """
    Deserializa datos usando el método especificado
    
    Args:
        data: Datos a deserializar
        method: 'json', 'pickle', 'pickle_base64', o 'hybrid'
    
    Returns:
        Datos deserializados
    """
    if method == 'json':
        return Serializer.deserialize_json(data)
    elif method == 'pickle':
        return Serializer.deserialize_pickle(data)
    elif method == 'pickle_base64':
        return Serializer.deserialize_pickle_base64(data)
    elif method == 'hybrid':
        return Serializer.deserialize_hybrid(data)
    else:
        raise ValueError(f"Método de deserialización desconocido: {method}")

