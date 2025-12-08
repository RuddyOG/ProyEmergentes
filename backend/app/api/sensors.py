from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field, validator
from typing import Any, Dict, List, Optional
from datetime import datetime
from db.mongo import get_mongo_collection
from routes.auth import get_current_user, require_gamc, require_admin

router = APIRouter(prefix="/api", tags=["sensors"])

# ============================================
# MODELOS DE DATOS
# ============================================

class SensorDataIngest(BaseModel):
    """Modelo para ingesta individual de datos de sensor"""
    sensor_type: str = Field(..., pattern="^(aire|sonido|soterrado)$")
    source_file: str
    row_number: int
    data: Dict[str, Any]
    
    @validator('data')
    def validate_data(cls, v, values):
        """Valida que los datos contengan campos mínimos requeridos"""
        if 'sensor_type' in values:
            sensor_type = values['sensor_type']
            required_fields = {
                'aire': ['object'],
                'sonido': ['object'],
                'soterrado': ['object']
            }
            if not any(field in v for field in required_fields.get(sensor_type, [])):
                raise ValueError(f"Datos incompletos para sensor tipo {sensor_type}")
        return v


class BulkSensorData(BaseModel):
    """Modelo para ingesta masiva de datos"""
    sensor_type: str = Field(..., pattern="^(aire|sonido|soterrado)$")
    source_file: str
    records: List[Dict[str, Any]]
    
    @validator('records')
    def validate_records(cls, v):
        if not v or len(v) == 0:
            raise ValueError("La lista de registros no puede estar vacía")
        if len(v) > 1000:
            raise ValueError("Máximo 1000 registros por solicitud")
        return v



# ENDPOINTS PÚBLICOS (SOLO LECTURA)


@router.get("/sensor/public", summary="Consulta pública de sensores (sin auth)")
def get_public_sensor_data(
    sensor_type: Optional[str] = Query(None, regex="^(aire|sonido|soterrado)$"),
    limit: int = Query(50, ge=1, le=100)
):
    """
    Consulta pública de datos de sensores (datos limitados, sin autenticación).
    
    - **sensor_type**: Filtrar por tipo de sensor
    - **limit**: Cantidad de registros (max: 100)
    
    Returns:
        dict: Lista limitada de registros públicos
    """
    if sensor_type:
        collections_to_query = [sensor_type]
    else:
        collections_to_query = ["aire", "sonido", "soterrado"]
    
    all_results = []
    
    for coll_name in collections_to_query:
        try:
            collection = get_mongo_collection(coll_name)
            cursor = collection.find({}, {
                "_id": 0,
                "time": 1,
                "sensor_type": 1,
                "object": 1,
                "deviceInfo.deviceName": 1
            }).limit(limit)
            
            for doc in cursor:
                doc["collection"] = coll_name
                all_results.append(doc)
        except Exception as e:
            print(f"Error consultando {coll_name}: {e}")
            continue
    
    return {
        "success": True,
        "count": len(all_results),
        "data": all_results,
        "note": "Datos públicos limitados. Autentícate para acceso completo."
    }


@router.get("/sensor/stats/public", summary="Estadísticas públicas")
def get_public_stats():
    """
    Obtiene estadísticas generales públicas del sistema (sin autenticación).
    
    Returns:
        dict: Estadísticas generales
    """
    stats = {}
    
    for sensor_type in ["aire", "sonido", "soterrado"]:
        try:
            collection = get_mongo_collection(sensor_type)
            stats[sensor_type] = {
                "total_records": collection.count_documents({}),
                "active_devices": len(collection.distinct("deviceInfo.deviceName"))
            }
        except:
            stats[sensor_type] = {"total_records": 0, "active_devices": 0}
    
    return {
        "success": True,
        "stats": stats,
        "last_update": datetime.utcnow().isoformat()
    }



# ENDPOINTS DE INGESTA (REQUIEREN AUTH GAMC)


@router.post("/ingest", summary="Ingesta individual (requiere rol GAMC o Admin)")
def ingest_single_sensor(
    payload: SensorDataIngest,
    current_user: dict = Depends(require_gamc)
):
    """
    Recibe un registro individual de sensor y lo almacena.
    
    **Requiere autenticación con rol GAMC o Admin**
    
    - **sensor_type**: Tipo de sensor (aire, sonido, soterrado)
    - **source_file**: Nombre del archivo de origen
    - **row_number**: Número de fila
    - **data**: Datos del sensor
    
    Returns:
        dict: Confirmación de inserción
    """
    collection_map = {
        "aire": "aire",
        "sonido": "sonido",
        "soterrado": "soterrado",
    }
    
    collection_name = collection_map[payload.sensor_type]
    
    document = {
        "sensor_type": payload.sensor_type,
        "source_file": payload.source_file,
        "row_number": payload.row_number,
        "ingested_at": datetime.utcnow(),
        "ingested_by": current_user["username"],
        **payload.data
    }
    
    try:
        collection = get_mongo_collection(collection_name)
        result = collection.insert_one(document)
        
        return {
            "success": True,
            "collection": collection_name,
            "inserted_id": str(result.inserted_id),
            "ingested_by": current_user["username"],
            "message": f"Registro insertado correctamente"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/ingest/bulk", summary="Ingesta masiva (requiere rol GAMC o Admin)")
def ingest_bulk_sensors(
    payload: BulkSensorData,
    current_user: dict = Depends(require_gamc)
):
    """
    Ingesta masiva de datos de sensores.
    
    **Requiere autenticación con rol GAMC o Admin**
    
    - **sensor_type**: Tipo de sensor
    - **source_file**: Archivo de origen
    - **records**: Lista de registros (max 1000)
    
    Returns:
        dict: Resumen de inserción
    """
    collection_map = {
        "aire": "aire",
        "sonido": "sonido",
        "soterrado": "soterrado",
    }
    
    collection_name = collection_map[payload.sensor_type]
    
    documents = []
    for idx, record in enumerate(payload.records):
        doc = {
            "sensor_type": payload.sensor_type,
            "source_file": payload.source_file,
            "row_number": idx + 1,
            "ingested_at": datetime.utcnow(),
            "ingested_by": current_user["username"],
            **record
        }
        documents.append(doc)
    
    try:
        collection = get_mongo_collection(collection_name)
        result = collection.insert_many(documents, ordered=False)
        
        return {
            "success": True,
            "collection": collection_name,
            "inserted_count": len(result.inserted_ids),
            "ingested_by": current_user["username"],
            "message": f"{len(result.inserted_ids)} registros insertados"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")



# ENDPOINTS DE CONSULTA (REQUIEREN AUTH)


@router.get("/sensor", summary="Consultar datos (requiere autenticación)")
def get_sensor_data(
    sensor_type: Optional[str] = Query(None, regex="^(aire|sonido|soterrado)$"),
    device_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """
    Consulta completa de datos de sensores.
    
    **Requiere autenticación**
    
    - **sensor_type**: Filtrar por tipo
    - **device_id**: Filtrar por dispositivo
    - **start_date/end_date**: Rango de fechas (ISO)
    - **limit**: Cantidad de registros
    - **skip**: Paginación
    
    Returns:
        dict: Lista completa de registros
    """
    if sensor_type:
        collections_to_query = [sensor_type]
    else:
        collections_to_query = ["aire", "sonido", "soterrado"]
    
    all_results = []
    
    for coll_name in collections_to_query:
        try:
            collection = get_mongo_collection(coll_name)
            
            query_filter = {}
            
            if device_id:
                query_filter["deviceInfo.deviceName"] = device_id
            
            if start_date or end_date:
                query_filter["time"] = {}
                if start_date:
                    try:
                        query_filter["time"]["$gte"] = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                    except:
                        pass
                if end_date:
                    try:
                        query_filter["time"]["$lte"] = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                    except:
                        pass
            
            cursor = collection.find(query_filter).skip(skip).limit(limit)
            
            for doc in cursor:
                doc["_id"] = str(doc["_id"])
                doc["collection"] = coll_name
                all_results.append(doc)
            
        except Exception as e:
            print(f"Error consultando {coll_name}: {e}")
            continue
    
    return {
        "success": True,
        "count": len(all_results),
        "skip": skip,
        "limit": limit,
        "requested_by": current_user["username"],
        "data": all_results
    }


@router.get("/sensor/stats/{sensor_type}", summary="Estadísticas detalladas (requiere auth)")
def get_sensor_stats(
    sensor_type: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Estadísticas completas de un tipo de sensor.
    
    **Requiere autenticación**
    
    Returns:
        dict: Estadísticas detalladas
    """
    if sensor_type not in ["aire", "sonido", "soterrado"]:
        raise HTTPException(status_code=400, detail="Tipo de sensor inválido")
    
    try:
        collection = get_mongo_collection(sensor_type)
        
        total_docs = collection.count_documents({})
        last_record = collection.find_one(sort=[("_id", -1)])
        unique_devices = len(collection.distinct("deviceInfo.deviceName"))
        
        # Estadísticas por dispositivo
        pipeline = [
            {
                "$group": {
                    "_id": "$deviceInfo.deviceName",
                    "count": {"$sum": 1},
                    "last_update": {"$max": "$time"}
                }
            }
        ]
        device_stats = list(collection.aggregate(pipeline))
        
        return {
            "success": True,
            "sensor_type": sensor_type,
            "total_records": total_docs,
            "unique_devices": unique_devices,
            "last_update": last_record.get("time") if last_record else None,
            "devices": device_stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")



# ENDPOINTS ADMINISTRATIVOS (SOLO ADMIN)


@router.delete("/sensor/{sensor_type}", summary="Eliminar datos (solo Admin)")
def delete_sensor_data(
    sensor_type: str,
    device_id: Optional[str] = None,
    confirm: bool = Query(False),
    admin_user: dict = Depends(require_admin)
):
    """
    Elimina registros de sensores.
    
    **Requiere rol Admin**
    
    - **sensor_type**: Tipo de sensor
    - **device_id**: Opcional - dispositivo específico
    - **confirm**: Debe ser true
    
    Returns:
        dict: Confirmación de eliminación
    """
    if sensor_type not in ["aire", "sonido", "soterrado"]:
        raise HTTPException(status_code=400, detail="Tipo inválido")
    
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Debe confirmar con confirm=true"
        )
    
    try:
        collection = get_mongo_collection(sensor_type)
        
        delete_filter = {}
        if device_id:
            delete_filter["deviceInfo.deviceName"] = device_id
        
        result = collection.delete_many(delete_filter)
        
        return {
            "success": True,
            "sensor_type": sensor_type,
            "deleted_count": result.deleted_count,
            "deleted_by": admin_user["username"],
            "message": f"{result.deleted_count} registros eliminados"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/sensor/audit", summary="Registro de auditoría (solo Admin)")
def get_audit_log(
    limit: int = Query(100, ge=1, le=500),
    admin_user: dict = Depends(require_admin)
):
    """
    Obtiene registros de auditoría de ingestas.
    
    **Requiere rol Admin**
    
    Returns:
        dict: Logs de auditoría
    """
    audit_logs = []
    
    for sensor_type in ["aire", "sonido", "soterrado"]:
        try:
            collection = get_mongo_collection(sensor_type)
            
            # Buscar registros con información de ingesta
            cursor = collection.find(
                {"ingested_by": {"$exists": True}},
                {
                    "sensor_type": 1,
                    "ingested_by": 1,
                    "ingested_at": 1,
                    "source_file": 1
                }
            ).sort([("ingested_at", -1)]).limit(limit)
            
            for doc in cursor:
                doc["_id"] = str(doc["_id"])
                audit_logs.append(doc)
        except:
            continue
    
    # Ordenar por fecha
    audit_logs.sort(key=lambda x: x.get("ingested_at", ""), reverse=True)
    
    return {
        "success": True,
        "count": len(audit_logs),
        "logs": audit_logs[:limit]
    }