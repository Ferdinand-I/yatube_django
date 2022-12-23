# Проект Yatube <img src="https://www.pinclipart.com/picdir/big/530-5305941_youtube-logo-computer-icons-black-transparent-youtube-icon.png" width=32>

*Yatube* - это блог для публикации тематических записей с возможностью загрузки изображений, написанный на **Django** и **HTML.**

Функционал приложения:
* Регистрация и аутентификация пользователей
* Смена пароля
* Создание, редактирование и удаление записей
* Загрузка изображений и публикация их вместе с постами
* Возможность подписаться/отписаться на/от избранных авторов
* Возможность просмотра детальной информации о пользователе
* Возможность просмотра всех тематических записей

Что реализовано в коде:
* Использование встроенных возможностей **Django** для управления админкой
* Использование встроенных возможностей **Django** для управления аккаунтом
* Описание моделей и форм
* Взаимодействие с БД **SQLite** с помощью **Django ORM**
* Рендер **HTML** шаблонов с помощью движка **Django templates**
* Документация и покрытие тестами с помощью встроенного **Django** модуля *django.test*
* Использование объектов пагинатора **Django**

Проект разрабатывался на версии <b>Python 3.7</b> и <b>Django 2.2.16</b>, также для запуска потребуется установить все необходимые зависимости *requirements.txt*

Чтобы запустить проект локально:

1. Клонируйте репозиторий себе на компьютер, находясь в директории, откуда вы хотите в будущем запускать проект (в примере испоьзуется ссылка для подключения с помощью протокола **SSH** в консоли **BASH** для **WINDOWS**)

```BASH
git clone git@github.com:Ferdinand-I/yatube_django.git
```

2. Создайте и активируйте виртуальное окружение (в примере используется утилита **venv**), перейдите в директорию проекта

```BASH
python -m venv venv
source venv/Scripts/activate
cd yatube_django
```

3. Обновите **PIP** и установите зависимости *requirements.txt*

```BASH
python -m pip install --upgrade pip
pip install -r requirements.txt
```

4. Перейдите в корневую директорию джанго проекта и сделайте миграции

```BASH
cd yatube
python manage.py migrate
```

5. Загрузите тестовые данные в БД

```BASH
python manage.py loaddata dump.json
```

6. Для доступа к админке сайта создайте суперпользователя

```BASH
python manage.py createsuperuser
```

7. Запустите проект на локальном сервере разработчика

```BASH
python manage.py runserver
```

Приложение будет доступно по <a href="http://127.0.0.1:8000">этому</a> адресу

Админка будет доступна по <a href="http://127.0.0.1:8000/admin/">этому</a>
