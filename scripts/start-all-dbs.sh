#!/bin/bash

echo "=========================================="
echo "ЗАПУСК ВСЕХ БАЗ ДАННЫХ"
echo "=========================================="

cd ~/Documents/my-dok-sever/2026/

# Создаём папку для инициализации SQL
mkdir -p init-sql
mkdir -p init-mongo

# Запускаем контейнеры
docker-compose -f docker-compose-lab.yml up -d

echo ""
echo "Ожидаем запуск баз данных (10 секунд)..."
sleep 10

echo ""
echo "=========================================="
echo "СТАТУС КОНТЕЙНЕРОВ"
echo "=========================================="
docker ps

echo ""
echo "=========================================="
echo "ПОДКЛЮЧЕНИЕ К БАЗАМ ДАННЫХ"
echo "=========================================="
echo ""
echo "📦 PostgreSQL:"
echo "   docker exec -it postgres_lab psql -U admin -d app_db"
echo ""
echo "⚡ Redis:"
echo "   docker exec -it redis_lab redis-cli -a redis123"
echo ""
echo "📝 MongoDB:"
echo "   docker exec -it mongo_lab mongosh -u admin -p mongo123"
echo ""
echo "🕸️ Neo4j:"
echo "   Веб-интерфейс: http://localhost:7474"
echo "   Логин: neo4j, пароль: neo4j123"
echo ""

chmod +x start-all-dbs.sh