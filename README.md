# Модели ML в продакшн. Домашнее задание 3
Этот репозиторий учебный, поэтому модели хранятся в нем. В продакшн окружении, модели бы брались из model registry (например, mlflow). 

**Краткое описание проекта:** применение стратегии безопасного развертывания (Blue-Green) для ML-моделей и автоматизирование процесса деплоя через CI/CD (GitHub Actions) на датасете Iris.

## Локальное использование
**Команды сборки и запуска:** для использования необходимо
- склонировать данный репозиторий с помощью `git clone` и зайти в соответствующую папку `cd mlops_hw3_Prisiazhniuk_Artem`
- иметь установленные docker, nginx
- запустить docker compose через `docker compose -f docker-compose.blue.yml -f docker-compose.green.yml -f docker-compose.nginx.yml up -d`
- теперь сервис работает по адресу localhost:8086 и отдельные контейнеры по адресам localhost:8081 (blue) и localhost:8082 (green), модели меняются в зависимости от текущего перенаправления

**Примеры вызовов /health и /predict:**
Чтобы выполнить запрос /health, достаточно использовать `curl localhost:8086/health`, ожидаемый результат `{"status":"ok","app_version":"blue","version":"v1.0.0"}`

Чтобы выполнить запрос /predict, достаточно использовать `curl -X POST "http://localhost:8086/predict" -H "Content-Type: application/json" -d '{"x": [1, 2, 3, 4]}'`, ожидаемый результат `{"status":"ok","prediction":2,"confidence":0.65,"app_version":"blue","version":"v1.0.0"}`

Посмотреть логи модели можно используя `docker exec -it <container_name> cat logs/app.log`