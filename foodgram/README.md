# foodgram-project

«Продуктовый помощник» (Проект Яндекс.Практикум) 
ip - 84.201.160.50
## Описание

Это онлайн-сервис, где пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Запуск (docker)

Запустить docker-compose:

`docker-compose up -d --build`

При первом запуске для функционирования проекта обязательно выполнить миграции:

`docker-compose exec web python manage.py migrate`

Чтобы загрузить список ингредиентов в БД:

`docker-compose exec web python manage.py loaddata ingredients.json`


------------
# Eng-Version

# foodgram-project

"Grocery Assistant" (The Yandex Project.Workshop)
ip-84.201.160.50
# # Description

This is an online service where users can publish recipes, subscribe to other users ' publications, add their favorite recipes to the Favorites list, and download a summary list of products needed to prepare one or more selected dishes before going to the store.

## Launch (docker)

Run docker-compose:

`docker-compose up -d --build`

At the first launch, you must perform migrations for the project to function:

`docker-compose exec web python manage.py migrate`
