# Сайт для поиска погоды на основе онлайн сервиса OpenWeatherMap

## Что реализовано:
- Подсказки для ввода города из встроенного api `openweathermap.org`
- История поиска последних городов
- Почасовая погода на сутки вперед
- Кэширование на 15 минут

# Как запустить
- Скачайте код
```
git clone https://github.com/Evgan4ik/weather_project.git
cd weather_project
```
- Установите зависимости
```
pip install -r requirements.txt
```
- Зарегистрируйтесь на сайте `openweathermap.org` и получите токен
- Создайте в корне файл `.env` c содержимым `OPENWEATHER_API_KEY=ваш_токен`
- Создайте и примените миграции базы данных
```
python manage.py makemigrations

python manage.py migrate
```
-Запустите сервер
```
python manage.py runserver

```

