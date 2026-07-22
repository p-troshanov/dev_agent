# backend/core/routers/keys.py
import urllib.request
import json
import asyncio
from fastapi import APIRouter, Depends, Query
from backend.core.database import get_db
from backend.core.schemas import ApiKeyAdd
from backend.core.llm import key_cooldowns
from backend.core.auth import get_current_user

router = APIRouter(prefix="/api", tags=["keys"])

@router.get("/keys")
def get_api_keys(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    with get_db() as conn:
        with conn.cursor() as c:
            c.execute('SELECT id, provider, api_key, created_at FROM api_keys WHERE user_id = %s ORDER BY provider, id ASC', (user_id,))
            return [{"id": row[0], "provider": row[1], "api_key": row[2], "created_at": row[3]} for row in c.fetchall()]

@router.post("/keys")
def add_api_key(data: ApiKeyAdd, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    with get_db() as conn:
        with conn.cursor() as c:
            c.execute('INSERT INTO api_keys (user_id, provider, api_key) VALUES (%s, %s, %s)', (user_id, data.provider, data.api_key.strip()))
        conn.commit()
    return {"status": "ok"}

@router.delete("/keys/{key_id}")
def delete_api_key(key_id: int, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    with get_db() as conn:
        with conn.cursor() as c:
            c.execute('DELETE FROM api_keys WHERE id = %s AND user_id = %s', (key_id, user_id))
        conn.commit()
    return {"status": "ok"}

@router.get("/keys/status")
def get_keys_status():
    return key_cooldowns

def get_or_balance_sync(api_key: str):
    result = {}
    req_key = urllib.request.Request(
        "https://openrouter.ai/api/v1/auth/key", 
        headers={"Authorization": f"Bearer {api_key}"}
    )
    try:
        with urllib.request.urlopen(req_key, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            result["key_data"] = data.get("data", {})
    except Exception:
        result["key_data"] = {}
        
    req_credits = urllib.request.Request(
        "https://openrouter.ai/api/v1/credits", 
        headers={"Authorization": f"Bearer {api_key}"}
    )
    try:
        with urllib.request.urlopen(req_credits, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            result["credits_data"] = data.get("data", {})
    except Exception:
        result["credits_data"] = {}
        
    return result

@router.get("/keys/balances")
async def get_key_balances(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    balances = {}
    
    with get_db() as conn:
        with conn.cursor() as c:
            c.execute('SELECT id, api_key FROM api_keys WHERE user_id = %s AND provider = %s', (user_id, 'openrouter'))
            or_keys = c.fetchall()
            
    loop = asyncio.get_running_loop()
    for kid, key in or_keys:
        data_res = await loop.run_in_executor(None, get_or_balance_sync, key)
        if data_res:
            key_data = data_res.get("key_data", {})
            credits_data = data_res.get("credits_data", {})
            
            total_credits = credits_data.get("total_credits")
            total_usage = credits_data.get("total_usage")
            
            key_limit = key_data.get("limit")
            key_usage = key_data.get("usage")
            
            final_limit = None
            final_usage = None
            final_rem = None
            
            if total_credits is not None and total_usage is not None:
                final_limit = total_credits
                final_usage = total_usage
                final_rem = total_credits - total_usage
            elif key_limit is not None and key_usage is not None:
                final_limit = key_limit
                final_usage = key_usage
                final_rem = key_limit - key_usage
                
            balances[kid] = {
                "limit": final_limit,
                "usage": final_usage,
                "remaining_balance": final_rem,
                "is_free_tier": key_data.get("is_free_tier")
            }
            
    return balances

@router.get("/statistics")
def get_statistics(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    with get_db() as conn:
        with conn.cursor() as c:
            c.execute('''
                SELECT id, provider, key_id, model, tokens, created_at, agent_name, cost, task_id
                FROM llm_statistics 
                WHERE user_id = %s
                ORDER BY id DESC LIMIT 500
            ''', (user_id,))
            return [{
                "id": row[0], 
                "provider": row[1], 
                "key_id": row[2], 
                "model": row[3], 
                "tokens": row[4], 
                "created_at": row[5],
                "agent_name": row[6],
                "cost": row[7],
                "task_id": row[8]
            } for row in c.fetchall()]

@router.get("/statistics/aggregated")
def get_aggregated_statistics(
    period: str = Query("day", pattern="^(day|week|month)$"),
    group_by: str = Query("provider", pattern="^(provider|agent_name|key_id|task_id)$"),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["id"]
    with get_db() as conn:
        with conn.cursor() as c:
            if period == "day":
                date_trunc = "DATE(created_at)"
            elif period == "week":
                date_trunc = "DATE_TRUNC('week', created_at)::DATE"
            else:
                date_trunc = "DATE_TRUNC('month', created_at)::DATE"
                
            query = f"""
                SELECT {date_trunc} as period_date, {group_by}, SUM(tokens) as total_tokens, COUNT(id) as total_requests, SUM(cost) as total_cost
                FROM llm_statistics
                WHERE user_id = %s
                GROUP BY {date_trunc}, {group_by}
                ORDER BY period_date DESC
            """
            c.execute(query, (user_id,))
            rows = c.fetchall()
            
    res = []
    for r in rows:
        res.append({
            "period_date": str(r[0]),
            "group": str(r[1]) if r[1] is not None else "None",
            "total_tokens": r[2],
            "total_requests": r[3],
            "total_cost": r[4] or 0.0
        })
    return res
