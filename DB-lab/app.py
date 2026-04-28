#!/usr/bin/env python3
"""
Учебное приложение для работы с разными базами данных
PostgreSQL + Redis + MongoDB + Neo4j
"""

import redis
import psycopg2
import pymongo
from neo4j import GraphDatabase
import json
from datetime import datetime

# ===== Конфигурация подключений =====

# PostgreSQL
PG_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'app_db',
    'user': 'admin',
    'password': 'admin123'
}

# Redis
REDIS_CONFIG = {
    'host': 'localhost',
    'port': 6379,
    'password': 'redis123',
    'decode_responses': True
}

# MongoDB
MONGO_CONFIG = {
    'host': 'localhost',
    'port': 27017,
    'username': 'admin',
    'password': 'mongo123'
}

# Neo4j
NEO4J_CONFIG = {
    'uri': 'bolt://localhost:7687',
    'user': 'neo4j',
    'password': 'neo4j123'
}


# ===== Классы для работы с базами =====

class PostgresManager:
    """Управление PostgreSQL"""
    
    def __init__(self):
        self.conn = None
    
    def connect(self):
        self.conn = psycopg2.connect(**PG_CONFIG)
        return self.conn
    
    def create_users_table(self):
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                email VARCHAR(100),
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        self.conn.commit()
        print("✅ Таблица users создана в PostgreSQL")
    
    def add_user(self, name, email):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO users (name, email) VALUES (%s, %s) RETURNING id",
            (name, email)
        )
        user_id = cur.fetchone()[0]
        self.conn.commit()
        print(f"✅ Пользователь добавлен в PostgreSQL: id={user_id}")
        return user_id
    
    def get_user(self, user_id):
        cur = self.conn.cursor()
        cur.execute("SELECT id, name, email FROM users WHERE id = %s", (user_id,))
        return cur.fetchone()


class RedisManager:
    """Управление Redis (кеш)"""
    
    def __init__(self):
        self.client = None
    
    def connect(self):
        self.client = redis.Redis(**REDIS_CONFIG)
        self.client.ping()
        print("✅ Подключение к Redis установлено")
        return self.client
    
    def cache_user(self, user_id, user_data, ttl=60):
        """Сохраняет пользователя в кеш на ttl секунд"""
        key = f"user:{user_id}"
        self.client.setex(key, ttl, json.dumps(user_data))
        print(f"✅ Пользователь {user_id} сохранён в кеш Redis на {ttl} сек")
    
    def get_cached_user(self, user_id):
        """Получает пользователя из кеша"""
        key = f"user:{user_id}"
        data = self.client.get(key)
        if data:
            return json.loads(data)
        return None
    
    def increment_counter(self, key):
        """Увеличивает счётчик"""
        return self.client.incr(key)
    
    def get_counter(self, key):
        """Получает значение счётчика"""
        val = self.client.get(key)
        return int(val) if val else 0


class MongoManager:
    """Управление MongoDB (документы)"""
    
    def __init__(self):
        self.client = None
        self.db = None
    
    def connect(self):
        self.client = pymongo.MongoClient(
            f"mongodb://{MONGO_CONFIG['username']}:{MONGO_CONFIG['password']}@localhost:27017/"
        )
        self.db = self.client['app_db']
        print("✅ Подключение к MongoDB установлено")
        return self.db
    
    def add_log(self, action, user_id, details):
        """Добавляет лог действия в MongoDB"""
        log_entry = {
            'action': action,
            'user_id': user_id,
            'details': details,
            'timestamp': datetime.now()
        }
        result = self.db.logs.insert_one(log_entry)
        print(f"✅ Лог записан в MongoDB: {action}")
        return result.inserted_id
    
    def get_user_logs(self, user_id):
        """Получает все логи пользователя"""
        return list(self.db.logs.find({'user_id': user_id}))


class Neo4jManager:
    """Управление Neo4j (граф связей)"""
    
    def __init__(self):
        self.driver = None
    
    def connect(self):
        self.driver = GraphDatabase.driver(
            NEO4J_CONFIG['uri'],
            auth=(NEO4J_CONFIG['user'], NEO4J_CONFIG['password'])
        )
        print("✅ Подключение к Neo4j установлено")
        return self.driver
    
    def add_friendship(self, user_id_1, user_id_2):
        """Добавляет связь дружбы между пользователями"""
        with self.driver.session() as session:
            result = session.run(
                """
                MERGE (u1:User {id: $id1})
                MERGE (u2:User {id: $id2})
                MERGE (u1)-[:FRIEND]->(u2)
                MERGE (u2)-[:FRIEND]->(u1)
                RETURN u1.id, u2.id
                """,
                id1=user_id_1, id2=user_id_2
            )
            print(f"✅ Связь дружбы в Neo4j: {user_id_1} <-> {user_id_2}")
            return result.single()
    
    def get_friends(self, user_id):
        """Находит друзей пользователя"""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (u:User {id: $user_id})-[:FRIEND]->(friend)
                RETURN friend.id AS friend_id
                """,
                user_id=user_id
            )
            return [record['friend_id'] for record in result]


# ===== Демонстрация работы =====

def main():
    print("=" * 60)
    print("УЧЕБНОЕ ПРИЛОЖЕНИЕ - РАБОТА С БАЗАМИ ДАННЫХ")
    print("=" * 60)
    
    # 1. PostgreSQL (основная БД)
    print("\n📦 1. РАБОТА С POSTGRESQL")
    pg = PostgresManager()
    pg.connect()
    pg.create_users_table()
    
    # Добавляем пользователя
    user_id = pg.add_user("Dmitry", "dima@example.com")
    user_data = pg.get_user(user_id)
    print(f"   Данные из PostgreSQL: {user_data}")
    
    # 2. Redis (кеш)
    print("\n⚡ 2. РАБОТА С REDIS (КЕШ)")
    r = RedisManager()
    r.connect()
    
    # Кешируем пользователя
    user_dict = {'id': user_id, 'name': 'Dmitry', 'email': 'dima@example.com'}
    r.cache_user(user_id, user_dict, ttl=30)
    
    # Проверяем кеш
    cached = r.get_cached_user(user_id)
    print(f"   Из кеша Redis: {cached}")
    
    # Счётчик просмотров
    views = r.increment_counter(f"user:{user_id}:views")
    print(f"   Просмотров профиля: {views}")
    
    # 3. MongoDB (логи)
    print("\n📝 3. РАБОТА С MONGODB (ЛОГИ)")
    mongo = MongoManager()
    mongo.connect()
    
    mongo.add_log('user_created', user_id, {'method': 'api', 'source': 'cli'})
    mongo.add_log('profile_viewed', user_id, {'views': views})
    
    logs = mongo.get_user_logs(user_id)
    print(f"   Логов в MongoDB: {len(logs)}")
    
    # 4. Neo4j (граф связей)
    print("\n🕸️ 4. РАБОТА С NEO4J (ГРАФ)")
    neo = Neo4jManager()
    neo.connect()
    
    # Добавляем второго пользователя
    user2_id = pg.add_user("Admin", "admin@example.com")
    
    # Создаём связь дружбы
    neo.add_friendship(user_id, user2_id)
    
    # Находим друзей
    friends = neo.get_friends(user_id)
    print(f"   Друзья пользователя {user_id}: {friends}")
    
    print("\n" + "=" * 60)
    print("✅ ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("=" * 60)


if __name__ "__main__":
    main()

    