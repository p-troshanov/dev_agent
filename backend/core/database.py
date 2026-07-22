# backend/core/database.py
import time
import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from contextlib import contextmanager
from backend.core.config import POSTGRES_URL

# Глобальный пул подключений к PostgreSQL
db_pool = None

def init_db_pool():
    global db_pool
    if db_pool is None:
        max_retries = 10
        for attempt in range(max_retries):
            try:
                db_pool = ThreadedConnectionPool(1, 20, dsn=POSTGRES_URL)
                print("✅ Успешное подключение к БД.")
                break
            except Exception as e:
                print(f"⚠️ Ошибка подключения к БД (попытка {attempt + 1}/{max_retries}): {e}")
                time.sleep(3)
        else:
            raise Exception("Критическая ошибка: Не удалось подключиться к БД после нескольких попыток.")

def close_db_pool():
    global db_pool
    if db_pool:
        db_pool.closeall()
        db_pool = None

@contextmanager
def get_db():
    global db_pool
    if db_pool is None:
        init_db_pool()
        
    conn = None
    max_retries = 5
    
    for attempt in range(max_retries):
        try:
            conn = db_pool.getconn()
            
            # Проверка живости соединения (ping)
            try:
                with conn.cursor() as c:
                    c.execute("SELECT 1")
            except (psycopg2.OperationalError, psycopg2.InterfaceError):
                # Если соединение мертвое, отбрасываем его и берем/создаем новое
                db_pool.putconn(conn, close=True)
                conn = None
                continue
                
            break # Соединение успешно получено и работает
        except psycopg2.OperationalError as e:
            print(f"⚠️ Временная ошибка сети/DNS при получении соединения (попытка {attempt + 1}/{max_retries}): {e}")
            if conn:
                try:
                    db_pool.putconn(conn, close=True)
                except:
                    pass
                conn = None
            time.sleep(1)
            
    if conn is None:
        # Если все попытки исчерпаны, пробуем жестко пересоздать пул
        print("⚠️ Пул БД не смог выдать соединение. Пересоздаем пул...")
        try:
            db_pool.closeall()
        except:
            pass
        db_pool = None
        init_db_pool()
        conn = db_pool.getconn()

    try:
        yield conn
    finally:
        if conn:
            try:
                db_pool.putconn(conn)
            except (psycopg2.OperationalError, psycopg2.InterfaceError):
                db_pool.putconn(conn, close=True)
