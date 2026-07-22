# backend/tool_node/routers/fs.py
import os
from fastapi import APIRouter, HTTPException
from backend.tool_node.schemas import FileWritePayload, FileReadPayload
from backend.tool_node.utils import get_safe_path

router = APIRouter(prefix="/api/fs", tags=["fs"])

@router.post("/write")
async def write_file(payload: FileWritePayload):
    try:
        target_path = get_safe_path(payload.path, payload.user_id)
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(payload.content)
            
        return {"status": "ok", "message": f"Файл {payload.path} успешно сохранен."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/read")
async def read_file(payload: FileReadPayload):
    try:
        target_path = get_safe_path(payload.path, payload.user_id)
        if not os.path.exists(target_path):
            raise HTTPException(status_code=404, detail="Файл не найден.")
            
        if os.path.isdir(target_path):
            return {"status": "ok", "content": f"[СИСТЕМНОЕ УКАЗАНИЕ]: Указанный путь ({payload.path}) является директорией. Используй инструмент scan_project для её просмотра."}
            
        with open(target_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        return {"status": "ok", "content": content}
    except HTTPException:
        raise
    except UnicodeDecodeError:
        return {"status": "ok", "content": "[СИСТЕМНАЯ ОШИБКА]: Попытка прочитать бинарный файл (изображение, архив и т.д.) как текст. Чтение прервано. Тебе не нужно читать содержимое этого файла."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
