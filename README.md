# Foodgram - продуктовый помощник

Проект для публикации рецептов. Пользователи могут добавлять свои рецепты и просматривать рецепты других пользователей. Есть возможность добавить рецепт в избранное, подписаться на заинтересовавшего автора, добавить рецепт в список покупок.

Также есть возможность скачать в TXT формате список покупок. При скачивании списка, для удобства пользователей, вес/количество дублирующихся продуктов суммируются.

## Использованные технологии
- django3
- djangorestframework
- python3

## Запуск проекта
Склонировать репозиторий на компьютер
```
git@github.com:Helga61/foodgram-project-react.git
```

В директории backend/foodgram/ создать файл .env, наполнить по шаблону:
```
SECRET_KEY='testkey'
DEBUG = Falce
```

### Для локального запуска backend проекта:

В корневой директории:

* Cоздать и активировать виртуальное окружение:
```
python -m venv venv

source venv/Scripts/activate
```

* Установить зависимости из файла requirements.txt:
```
python -m pip install --upgrade pip

pip install -r requirements.txt
```

Перейти в директорию backend/

* Выполнить миграции:
```
python manage.py migrate
```

* Заполнить базу данных ингредиентами:
```
python manage.py import_ingredients
```

* Запустить проект:
```
python manage.py runserver
```

## Автор

Ольга Воронюк

# Примечание редакции

Полная версия ReadMe со ссылкой на ReDoc и примерами запросов API обязательно появится после развертывания проекта на сервере.