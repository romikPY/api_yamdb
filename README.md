# api_yamdb
## Описание
Проект разработан в результате совместной командной работы в одном репозитории. Цель проекта api_yamdb заключается в тестирование и отработка API для кастомной модели пользователей(Users), модели произведений(Title), модели жанры(Genre), категории(Category); отзывы на произведения(Reviews), комментарии к отзывам(Comments).

Приложение предусматривает 5 типов пользовательского доступа: аноним, зарегистрированный, модератор, администратор, суперпользователь.

## Установка
api yamdb
Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:

git clone https://github.com/romikpy/api_yamdb.git
cd api_yamdb
Cоздать и активировать виртуальное окружение:

python -m venv venv
source venv/scripts/activate
Установить зависимости из файла requirements.txt:

python -m pip install --upgrade pip
pip install -r requirements.txt

Выполнить миграции:

python manage.py migrate

Запустить проект:

python manage.py runserver

## Примеры работы с API
*Авторизация*:

POST api/v1/auth/signup/ - регистрация пользователей самостоятельно с письмом подтверждения на почту
POST /auth/token/ - получение токена доступа

*Доступно без авторизации*:

GET api/v1/categories/ - получить список всех категорий

GET api/v1/genres/ - получить список всех жанров

GET api/v1/titles/ - получить список всех произведений

GET api/v1/titles/{title_id}/ - получить произведение по id

GET api/v1/titles/{title_id}/reviews/ - получить список всех отзывов на произведение

GET api/v1/titles/{title_id}/reviews/{review_id}/ - получить отзывов по id на произведение

GET api/v1/titles/{title_id}/reviews/{review_id}/comments/ - получить список всех комментариев к отзыву

GET api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/ - получить комментарий по id к отзыву

При указании параметров limit и offset выдача фильтруется по количеству и началу для списков

*Доступно после автоизации*:

POST /api/v1/titles/{title_id}/reviews/ - добавить отзыв к произведению по номеру произведения

POST /api/v1/titles/{title_id}/reviews/{review_id}/comments/ - добавить комментарий к отзыву

(Также доступно модераторам, администраторам)

PATCH /api/v1/titles/{title_id}/reviews/{review_id}/ - обновление отзыва по id к конкретному произведению по id

PATCH /api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id} - обновление комментария по id

DELETE /api/v1/titles/{title_id}/reviews/{review_id}/ - удаление отзыва по id к конкретному произведению по id

DELETE /api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id} - удаление комментария по id

*С правом доступа администратор*:

GET api/v1/users/ - получить список всех пользователей

GET api/v1/users/{username}/ - получить пользователя по username

POST api/v1/categories/ - добавить категорию

POST api/v1/genres/ - добавить жанр

POST api/v1/titles/ - добавить произведение

DELETE api/v1/users/{username}/ - удалить пользователя по username

DELETE api/v1/categories/{slug} - удалить категорию по slug

DELETE api/v1/genres/{slug} - удалить жанр по slug

DELETE api/v1/titles/{title_id}/ - удалить произведение по id

PATCH api/v1/users/{username}/ - частично обновить информацию по username
PATCH /api/v1/titles/{titles_id}/ - частично обновить информацию у произведения по id
