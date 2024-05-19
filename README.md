
<h1 align="center">Продуктовый помощник FOODGRAM</h1>


<h2 align="center">Описание</h2>

<p>
    Foodgram - это сайт, с помощью которого, пользователи могут делиться своими рецептами с другими пользователями.
    Рецепты можно добавлять в избраное, можно создавать список покупок и подписываться на авторов рецептов.</p>
    <p>В списке покупок можно скачать `.txt` файл, со списком ингредиентов с указанием необходимого объёма покупок для выбранных блюд.
</p>

<h3 align="center">
    <a href="https://foodgramm.gotdns.ch/">Сайт "Продуктовый помощник"</a><p></p>
    <a href="https://foodgramm.gotdns.ch/api/docs/">Спецификация API</a>
</h3>


<h2>Запуск проекта:</h2>

```shell
# Склонировать репозиторий
git clone git@github.com:voven007/foodgram.git
```

> Для работоспособности проекта необходимо создать файл `.env` с переменными окружения в корневой директории проекта</br>
> В нем должны быть указаны следующие переменные окружения:

/POSTGRES_USER=**** </br>
/POSTGRES_PASSWORD=**** </br>
/POSTGRES_DB=**** </br>
/DB_HOST=**** </br>
/DB_PORT=**** </br>
/SECRET_KEY=**** </br>
/ALLOWED_HOSTS=**** </br>
/DEBUG_MODE=**** </br>


```shell
# Запустить докер композ
docker-compose.prodaction up
```

```bash
# Наполнение БД ингредиентами производится командой:
sudo docker compose -f docker-compose.production.yml exec python manage.py import
```
