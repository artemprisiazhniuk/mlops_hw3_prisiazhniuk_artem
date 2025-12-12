# Модели ML в продакшн. Домашнее задание 3
Этот репозиторий учебный, поэтому модели хранятся в нем. В продакшн окружении, модели бы брались из model registry (например, mlflow). 

**Краткое описание проекта:** применение стратегии безопасного развертывания (Blue-Green) для ML-моделей и автоматизирование процесса деплоя через CI/CD (GitHub Actions) на датасете Iris.



- [Выполнение с деплоем на облако](#выполнение-с-деплоем-на-облако)
- [Локальное выполнение](#локальное-выполнение)

## Выполнение с деплоем на облако
**Команды сборки и запуска:** для использования необходимо
- создать виртуальную машину на облаке (в нашем случае GCP)
- склонировать данный репозиторий с помощью `git clone` и зайти в соответствующую папку `cd mlops_hw3_Prisiazhniuk_Artem`
- установить docker, docker compose и зависимости из `requirementx.txt` для `deployer.py`
- запустить `python3 -m uvicorn deployer:app --host 0.0.0.0 --port 9000` (теперь VM ждет разворачивания от github actions)
- после push или перезапуска actions получаем запрос на deploy от github actions
- VM через скрипт запускает необходимые контейнеры
- теперь сервис работает по адресу VM на порте 8086 (по умолчанию работает версия blue)
- чтобы поменять версию (или сделать полный откат соответственно), необходимо
    - подменить `nginx.conf` на `nginx.<color>.conf`: `cp nginx/nginx.<color>.conf nginx/nginx.conf`
    - и перезагрузить балансировщик: `docker exec -it <nginx_container_name> nginx -s reload`
- для версии green реализованный автоматический временный откат при наличии ошибок, настроенный через max_fails и fail_timeout в конфиге nginx

**Примеры вызовов /health и /predict:**
Чтобы выполнить запрос /health, достаточно использовать `curl <VM_ip>:8086/health`, ожидаемый результат `{"status":"ok","app_version":"blue","version":"v1.0.0"}`

Чтобы выполнить запрос /predict, достаточно использовать `curl -X POST "http://<VM_ip>:8086/predict" -H "Content-Type: application/json" -d '{"x": [1, 2, 3, 4]}'`, ожидаемый результат `{"status":"ok","prediction":2,"confidence":0.65,"app_version":"blue","version":"v1.0.0"}`

Посмотреть логи модели можно используя `docker exec -it <container_name> cat logs/app.log`

Примеры запросов:
(при запущенных контейнерах на VM)
[VM](img/vm.png)

(запросы до и после изменения модели)
[Calls](img/calls.png)

(изменение на VM)
[Nginx](img/nginx.png)


## Локальное выполнение
**Команды сборки и запуска:** для использования необходимо
- склонировать данный репозиторий с помощью `git clone` и зайти в соответствующую папку `cd mlops_hw3_Prisiazhniuk_Artem`
- иметь установленные docker, nginx
- поменять в `docker-compose.blue.yml` и `docker-compose.green.yml` `image: ...` на `build: .`
- запустить docker compose через `docker compose -f docker-compose.blue.yml -f docker-compose.green.yml -f docker-compose.nginx.yml up -d`
- теперь сервис работает по адресу localhost:8086 и отдельные контейнеры по адресам localhost:8081 (blue) и localhost:8082 (green), модели меняются в зависимости от текущего перенаправления

**Примеры вызовов /health и /predict:**
Чтобы выполнить запрос /health, достаточно использовать `curl localhost:8086/health`, ожидаемый результат `{"status":"ok","app_version":"blue","version":"v1.0.0"}`

Чтобы выполнить запрос /predict, достаточно использовать `curl -X POST "http://localhost:8086/predict" -H "Content-Type: application/json" -d '{"x": [1, 2, 3, 4]}'`, ожидаемый результат `{"status":"ok","prediction":2,"confidence":0.65,"app_version":"blue","version":"v1.0.0"}`

Посмотреть логи модели можно используя `docker exec -it <container_name> cat logs/app.log`

