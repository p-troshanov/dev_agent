# backend/core/tasks/retriever.py
import json
from backend.core.database import get_db
from backend.core.llm import generate_response, extract_json

async def get_relevant_tools(task_description: str, user_id: int):
    """
    Кладовщик: читает активные инструменты пользователя из БД и просит быструю LLM
    выбрать только необходимые для конкретной задачи.
    Возвращает список схем и список названий.
    """
    with get_db() as conn:
        with conn.cursor() as c:
            c.execute('SELECT name, description, schema_json FROM user_tools WHERE is_active = 1 AND user_id = %s', (user_id,))
            all_tools = c.fetchall()

    if not all_tools:
        return [], []

    tools_info = []
    tools_map = {}
    for name, desc, schema_json_data in all_tools:
        tools_info.append(f"- {name}: {desc}")
        try:
            tools_map[name] = schema_json_data if isinstance(schema_json_data, dict) else json.loads(schema_json_data)
        except:
            pass

    tools_list_text = "\n".join(tools_info)

    sys_prompt = (
        "Ты системный Кладовщик. Твоя задача — проанализировать ТЗ пользователя и выбрать инструменты, "
        "которые понадобятся Инженеру для решения этой задачи. "
        "Выдавай ответ СТРОГО в виде чистого JSON-массива строк (только системные названия инструментов). "
        "Пример ответа: [\"read_file\", \"run_terminal\"]\n"
        "Если ни один инструмент не нужен, верни пустой массив [].\n\n"
        f"Доступные активные инструменты на складе:\n{tools_list_text}"
    )

    messages = [{"role": "user", "content": f"ТЗ: {task_description}"}]
    
    response = await generate_response(messages, system_prompt=sys_prompt, model_override=None, agent_name="Кладовщик", user_id=user_id)
    
    selected_schemas = []
    selected_names = []
    
    if response and response.choices:
        content = response.choices[0].message.content.strip()
        chosen_names = extract_json(content)
        
        if isinstance(chosen_names, list):
            for name in chosen_names:
                if name in tools_map:
                    selected_schemas.append(tools_map[name])
                    selected_names.append(name)
        elif isinstance(chosen_names, dict) and chosen_names:
            for k, v in chosen_names.items():
                if isinstance(v, list):
                    for name in v:
                        if name in tools_map:
                            selected_schemas.append(tools_map[name])
                            selected_names.append(name)
                    break
        
    if not selected_schemas:
        print("⚠️ [КЛАДОВЩИК] Не удалось распарсить ответ, выдаю все активные инструменты.")
        selected_schemas = list(tools_map.values())
        selected_names = list(tools_map.keys())

    return selected_schemas, selected_names
