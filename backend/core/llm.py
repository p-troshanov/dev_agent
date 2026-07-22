# backend/core/llm.py
import os
import json
import time
import re
import asyncio
from typing import Any
from litellm import acompletion
import litellm
from backend.core.database import get_db

litellm.suppress_debug_info = True
os.environ["OR_SITE_URL"] = "https://app.jetplan.site/"
os.environ["OR_APP_NAME"] = "RITA Core"

key_cooldowns = {
    "groq": {},
    "gemini": {},
    "openrouter": {}
}

def get_keys_from_db(provider: str, user_id: int) -> list:
    try:
        with get_db() as conn:
            with conn.cursor() as c:
                c.execute("SELECT id, api_key FROM api_keys WHERE provider = %s AND user_id = %s", (provider, user_id))
                return [{"id": row[0], "key": row[1]} for row in c.fetchall()]
    except Exception as e:
        print(f"Ошибка получения ключей из БД: {e}", flush=True)
        return []

def log_llm_request(provider: str, key_id: int, model: str, tokens: int, agent_name: str = None, user_id: int = None, cost: float = 0.0, task_id: int = None):
    if not user_id:
        return
    try:
        with get_db() as conn:
            with conn.cursor() as c:
                c.execute(
                    "INSERT INTO llm_statistics (user_id, provider, key_id, model, tokens, agent_name, cost, task_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (user_id, provider, key_id, model, tokens, agent_name, cost, task_id)
                )
            conn.commit()
    except Exception as e:
        print(f"Ошибка записи статистики LLM: {e}", flush=True)

def parse_groq_cooldown(error_str: str) -> float:
    match = re.search(r'try again in (?:(\d+)m)?([\d\.]+)s', error_str)
    if match:
        mins = int(match.group(1)) if match.group(1) else 0
        secs = float(match.group(2))
        return mins * 60 + secs
    return 600

def _extract_total_tokens(usage_obj):
    if not usage_obj:
        return 0
    if isinstance(usage_obj, dict):
        return usage_obj.get('total_tokens', 0)
    return getattr(usage_obj, 'total_tokens', 0)

def _calculate_cost(provider, model_name, usage_obj):
    if provider in ["groq", "gemini"]:
        return 0.0
    try:
        p_tok, c_tok = 0, 0
        if usage_obj:
            if isinstance(usage_obj, dict):
                p_tok = usage_obj.get('prompt_tokens', 0)
                c_tok = usage_obj.get('completion_tokens', 0)
            else:
                p_tok = getattr(usage_obj, 'prompt_tokens', 0)
                c_tok = getattr(usage_obj, 'completion_tokens', 0)
                
        return litellm.completion_cost(
            model=model_name,
            prompt_tokens=p_tok,
            completion_tokens=c_tok
        ) or 0.0
    except Exception as e:
        print(f"[LLM] Ошибка вычисления стоимости для {model_name}: {e}", flush=True)
        return 0.0

async def generate_response(messages, system_prompt=None, tools=None, model_override=None, agent_name=None, user_id=None, task_id=None, stream_callback=None, is_cancelled=None, **extra_kwargs):
    full_messages = []
    if system_prompt:
        full_messages.append({"role": "system", "content": system_prompt})
    full_messages.extend(messages)
    
    default_pipeline = [
        {"provider": "groq", "name": "groq/llama-3.3-70b-versatile"},
        {"provider": "gemini", "name": "gemini/gemini-3.5-flash"},
        {"provider": "openrouter", "name": "openrouter/meta-llama/llama-3.1-8b-instruct"},
        {"provider": "gemini", "name": "gemini/gemini-3.1-flash"}
    ]
    model_pipeline = []
    
    if model_override:
        if "/" in model_override:
            provider = model_override.split("/")[0]
            override_entry = {"provider": provider, "name": model_override}
        else:
            filtered = [m for m in default_pipeline if m["provider"] == model_override]
            if filtered:
                override_entry = filtered[0]
            else:
                override_entry = {"provider": model_override, "name": model_override}
                
        model_pipeline.append(override_entry)
        for m in default_pipeline:
            if m["name"] != override_entry["name"]:
                model_pipeline.append(m)
    else:
        model_pipeline = default_pipeline

    for target in model_pipeline:
        provider = target["provider"]
        model_name = target["name"]
        
        api_kwargs = {"model": model_name, "messages": full_messages, "timeout": 120}
        
        if tools:
            api_kwargs["tools"] = tools
            api_kwargs["tool_choice"] = "auto"
            
        if stream_callback:
            api_kwargs["stream"] = True
            api_kwargs["stream_options"] = {"include_usage": True}
            
        api_kwargs.update(extra_kwargs)
        
        keys_data = get_keys_from_db(provider, user_id)
        if not keys_data:
            env_key = os.getenv(f"{provider.upper()}_API_KEY")
            if env_key:
                keys_data = [{"id": None, "key": env_key}]
                
        if not keys_data:
            continue
            
        success = False
        for idx, key_info in enumerate(keys_data):
            key = key_info["key"]
            key_id = key_info["id"]
            
            max_retries = 3
            for attempt in range(max_retries):
                cooldown_until = key_cooldowns[provider].get(key, 0)
                
                if time.time() < cooldown_until:
                    break
                    
                try:
                    api_kwargs["api_key"] = key
                    response = await acompletion(**api_kwargs)
                    
                    if stream_callback:
                        reconstructed = await _handle_stream(response, stream_callback, is_cancelled)
                        usage_obj = getattr(reconstructed, 'usage', None)
                        
                        t_tok = _extract_total_tokens(usage_obj)
                        cost = _calculate_cost(provider, model_name, usage_obj)
                        
                        log_llm_request(provider, key_id, model_name, t_tok, agent_name, user_id, cost, task_id)
                        return reconstructed
                        
                    usage_obj = getattr(response, 'usage', None)
                    t_tok = _extract_total_tokens(usage_obj)
                    cost = _calculate_cost(provider, model_name, usage_obj)
                    
                    log_llm_request(provider, key_id, model_name, t_tok, agent_name, user_id, cost, task_id)
                    
                    success = True
                    return response
                    
                except Exception as e:
                    error_str = str(e).lower()
                    print(f"Ошибка [LLM] Провайдер {provider} ({model_name}) попытка {attempt+1}/{max_retries}: {e}", flush=True)
                    
                    if provider == "groq":
                        if "rate limit" in error_str or "429" in error_str:
                            wait_time = parse_groq_cooldown(error_str)
                            key_cooldowns["groq"][key] = time.time() + wait_time
                            break
                    elif provider == "gemini":
                        if any(kw in error_str for kw in ["429", "403", "503", "limit", "quota"]):
                            key_cooldowns["gemini"][key] = time.time() + 3600
                            break
                    elif provider == "openrouter":
                        if any(kw in error_str for kw in ["429", "limit", "rate"]):
                            if attempt < max_retries - 1:
                                await asyncio.sleep(4)
                                continue
                            else:
                                key_cooldowns["openrouter"][key] = time.time() + 60
                                break
                                
                    if attempt < max_retries - 1:
                        await asyncio.sleep(3)
                        continue
                    else:
                        break
                        
            if success:
                break
        if success:
            break
            
    print("Все провайдеры исчерпаны, fallback не удался.", flush=True)
    return None

async def _handle_stream(response_stream, stream_callback, is_cancelled=None):
    full_content = ""
    tool_calls_dict = {}
    usage = None
    
    async for chunk in response_stream:
        if is_cancelled and is_cancelled():
            break
            
        if hasattr(chunk, 'usage') and chunk.usage:
            usage = chunk.usage
        if not getattr(chunk, "choices", None):
            continue
            
        delta = chunk.choices[0].delta
        
        if getattr(delta, "content", None):
            full_content += delta.content
            await stream_callback(delta.content)
            
        if getattr(delta, "tool_calls", None):
            for tc in delta.tool_calls:
                idx = getattr(tc, "index", 0)
                if idx not in tool_calls_dict:
                    tool_calls_dict[idx] = {
                        "id": getattr(tc, "id", f"call_{idx}"),
                        "type": "function",
                        "function": {
                            "name": getattr(tc.function, "name", "") if hasattr(tc, "function") else "",
                            "arguments": getattr(tc.function, "arguments", "") if hasattr(tc, "function") else ""
                        }
                    }
                else:
                    if hasattr(tc, "function"):
                        if getattr(tc.function, "name", None):
                            tool_calls_dict[idx]["function"]["name"] += tc.function.name
                        if getattr(tc.function, "arguments", None):
                            tool_calls_dict[idx]["function"]["arguments"] += tc.function.arguments

    class MockFunc:
        def __init__(self, name, arguments):
            self.name, self.arguments = name, arguments
    class MockTC:
        def __init__(self, id, func):
            self.id, self.function = id, func
    class MockMsg:
        def __init__(self, content, tcs):
            self.content, self.tool_calls = content, tcs
    class MockChoice:
        def __init__(self, msg):
            self.message = msg
    class MockResp:
        def __init__(self, choices, usage):
            self.choices = choices
            self.usage = usage

    tcs = []
    for k in sorted(tool_calls_dict.keys()):
        tcs.append(MockTC(tool_calls_dict[k]["id"], MockFunc(tool_calls_dict[k]["function"]["name"], tool_calls_dict[k]["function"]["arguments"])))
        
    return MockResp([MockChoice(MockMsg(full_content if full_content else None, tcs if tcs else None))], usage)

def extract_json(text: str) -> Any:
    text = text.strip()
    try: return json.loads(text)
    except Exception: pass
    
    try:
        match = re.search(r'`{3}(?:json)?\s*(.*?)\s*`{3}', text, re.DOTALL)
        if match: return json.loads(match.group(1))
    except Exception: pass
    
    try:
        start_idx = text.find('[')
        end_idx = text.rfind(']')
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            return json.loads(text[start_idx:end_idx+1])
    except Exception: pass

    try:
        start_idx = text.find('{')
        end_idx = text.rfind('}')
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            return json.loads(text[start_idx:end_idx+1])
    except Exception: pass
    
    return {}
