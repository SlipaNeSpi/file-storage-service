import psycopg2
import traceback

try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="file_storage",
        user="postgres",
        password="123"
    )
    print("✅ Подключение успешно!")
    conn.close()
except Exception as e:
    print(f"❌ Ошибка: {e}")
    print(f"Тип ошибки: {type(e)}")
    traceback.print_exc()
