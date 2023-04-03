# FastAPI Playground

## Описание
* Проект для изучения FastAPI, SQLAclhemy, Alembic.
* За основу взято [тестовое задание](https://github.com/avito-tech/internship_backend_2022) из Авито (то, что оно на golang, в данном случае ни на что не влияет, т.к нужно было найти какое то ТЗ с чёткими задачами и целями).
* В качестве ориентира для структуры использовалась статья [Camillio Visni](https://camillovisini.com/article/abstracting-fastapi-services/)

## Запуск
1. Создать виртуальное окружение
2. `pip install -r requirements`
3. `make run`


## API
* __GET__ `/`: root
* __GET__ `/api/users/`: Список всех Пользователей
* __POST__ `/api/users/`: Создать Пользователя
* __GET__ `/api/users/{user_ud}`: Получение Пользователя по ID
* __POST__ `/api/users/{user_ud}/add_money/`: Зачислить средства на баланс Пользователя
* __POST__ `/api/users/{user_ud}/reserve/`: Зарезервировать средства
* __POST__ `/api/users/{user_ud}/confirm/`: Подтвердить оплату, снять указанное количество средств с резерва и создать Транзакцию
* __POST__ `/api/users/{user_ud}/reset_reserve/`: Перенести все деньги из резерва в баланс
* __GET__ `/api/transactions/`: Список всех Транзакций
* __GET__ `/api/transactions/{user_id}`: Получение Транзакции по ID
* __GET__ `/api/transactions/services_statistics`: Статистика по Услугам на основании Транзакций


## Стек
* FastAPI
* SQLAlchemy
* Alembic
* SQLite


## Референсы
* https://camillovisini.com/article/abstracting-fastapi-services/
* https://github.com/avito-tech/internship_backend_2022

