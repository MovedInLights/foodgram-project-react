# Социальная сеть "Foodgram"

## Описание

На этом сайте вы можете создавать рецепты, подписываться на других авторов,
добавлять рецепты этих авторов в избранное или в корзину. Корзину можно конвертировать
в перечень товаров для похода в магазин. Очень удобно!

## Технологии

Использованные технологии можно посмотреть в файле requirements.txt

## Запуск проекта

Установите и активируйте виртуальное окружение
Установите зависимости из файла requirements.txt

    pip install -r requirements.txt

В папке с файлом manage.py выполните команду:

    python3 manage.py runserver

Чтобы развернуть сервис при помощи Docker, выполните следующие команды: 
Убедитесь, что вы находитесь в той же директории infra, 
и запустите сборку образа:

    sudo docker-compose up -d --build 

Остановить запущенный контейнер:

    docker container stop <CONTAINER ID>

Запустить собранный контейнер

    docker container start <CONTAINER ID> 

Список всех команд для работы с контейнером можно вызвать через:

    docker container

    docker compose

Посмотреть версию Docker:

    docker-compose --version

Создание и запуск контейнеров:

    docker-compose up -d

Остановить контейнеры:

    docker-compose down

### Команды, которые могут помочь вам.

Сделать миграции:

    docker-compose exec web python manage.py migrate 

Создать супер пользователя:

    docker-compose exec web python manage.py createsuperuser

Собрать статику и подключить ее к проекту:

    docker-compose exec web python manage.py collectstatic --no-input

Загрузить данные базы в json файл:

    docker-compose exec web manage.py dumpdata > dump.json

### Фикстуры

Вы можете заполнить проект подготовленными для вас данными ингридиентов. 
Для этого исполните команду:

    docker-compose exec web python manage.py fill_the_base

### IP развернутого приложения и админская учетка

    http://51.250.25.9
    http://51.250.25.9/admin
    Login: Alekudryavtsev@gmail.com
    Pass: asde1234


### Авторы

Команда практикума и Алексей Кудрявцев