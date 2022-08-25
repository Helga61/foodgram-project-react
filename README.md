[![Foodgram workflow](https://github.com/Helga61/foodgram-project-react/actions/workflows/foodgram.yml/badge.svg)](https://github.com/Helga61/foodgram-project-react/actions/workflows/foodgram.yml)

# Foodgram - продуктовый помощник

Проект для публикации рецептов. Пользователи могут добавлять свои рецепты и просматривать рецепты других пользователей. Есть возможность добавить рецепт в избранное, подписаться на заинтересовавшего автора, добавить рецепт в список покупок.

Также есть возможность скачать в TXT формате список покупок. При скачивании списка, для удобства пользователей, вес/количество дублирующихся продуктов суммируются.

Проект доступен по адресу http://84.201.140.27
## Использованные технологии
- django3
- djangorestframework
- python3
- PostgreSQL
- gunicorn
- nginx

## Запуск проекта на сервере
- Войти на сервер, установить docker и docker-compose
```
sudo apt install docker.io
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

- Склонировать репозиторий
```
git@github.com:Helga61/foodgram-project-react.git
```

- В файле nginx.conf укажите свой IP

- В директории infra/ создать файл .env, наполнить по шаблону:
```
SECRET_KEY='testkey'
DEBUG = Falce
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

* Перейти в директорию foodgram-project-react/infra/

* Собрать и запустить проект
```
sudo docker-compose up -d --build
```

Выполнить миграции, создать суперпользователя, подгрузить статику, наполнить базу ингредиентами
```
sudo docker-compose exec backend python manage.py migrate
sudo docker-compose exec backend python manage.py createsuperuser
sudo docker-compose exec backend python manage.py collectstatic
sudo docker-compose exec backend python manage.py import_ingredients
```

## Документация API

Документация API доступна по адресу http://51.250.30.75//redoc/

### Примеры работы с API:

- Получение списка рецептов (Доступно незарегистрированному пользователю)

Запрос
```
GET http://localhost/api/recipes/
```
Ответ
```
{
  "count": 123,
  "next": "http://foodgram.example.org/api/recipes/?page=4",
  "previous": "http://foodgram.example.org/api/recipes/?page=2",
  "results": [
    {
      "id": 0,
      "tags": [
        {
          "id": 0,
          "name": "Завтрак",
          "color": "#E26C2D",
          "slug": "breakfast"
        }
      ],
      "author": {
        "email": "user@example.com",
        "id": 0,
        "username": "string",
        "first_name": "Вася",
        "last_name": "Пупкин",
        "is_subscribed": false
      },
      "ingredients": [
        {
          "id": 0,
          "name": "Картофель отварной",
          "measurement_unit": "г",
          "amount": 1
        }
      ],
      "is_favorited": true,
      "is_in_shopping_cart": true,
      "name": "string",
      "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
      "text": "string",
      "cooking_time": 1
    }
  ]
}
```
- Создание рецепта (доступно зарегестированному пользователю)Ж

Запрос
```
POST http://localhost/api/recipes/
```
Параметры запроса
```
{
  "ingredients": [
    {
      "id": 1123,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}
```
Ответ
```
{
  "id": 0,
  "tags": [
    {
      "id": 0,
      "name": "Завтрак",
      "color": "#E26C2D",
      "slug": "breakfast"
    }
  ],
  "author": {
    "email": "user@example.com",
    "id": 0,
    "username": "string",
    "first_name": "Вася",
    "last_name": "Пупкин",
    "is_subscribed": false
  },
  "ingredients": [
    {
      "id": 0,
      "name": "Картофель отварной",
      "measurement_unit": "г",
      "amount": 1
    }
  ],
  "is_favorited": true,
  "is_in_shopping_cart": true,
  "name": "string",
  "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
  "text": "string",
  "cooking_time": 1
}
```

- Подписки
(Возвращает пользователей, на которых подписан текущий пользователь. В выдачу добавляются рецепты)

Запрос 
```
GET http://localhost/api/users/subscriptions/
```
Ответ
```
{
  "count": 123,
  "next": "http://foodgram.example.org/api/users/subscriptions/?page=4",
  "previous": "http://foodgram.example.org/api/users/subscriptions/?page=2",
  "results": [
    {
      "email": "user@example.com",
      "id": 0,
      "username": "string",
      "first_name": "Вася",
      "last_name": "Пупкин",
      "is_subscribed": true,
      "recipes": [
        {
          "id": 0,
          "name": "string",
          "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
          "cooking_time": 1
        }
      ],
      "recipes_count": 0
    }
  ]
}
```
## Автор пректа

Ольга Воронюк

