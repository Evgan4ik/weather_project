import requests
from datetime import datetime, timedelta
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.cache import cache_page
from django.core.cache import cache


@cache_page(60 * 15)
def weather_search(request):
    weather_data = None
    error = None
    history = request.session.get('weather_search_history', [])[:5]

    if request.method == 'POST':
        city = request.POST.get('city', '')

        try:
            current_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={settings.OPENWEATHER_API_KEY}&units=metric&lang=ru"
            forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={settings.OPENWEATHER_API_KEY}&units=metric&lang=ru"

            current_response = requests.get(current_url)
            forecast_response = requests.get(forecast_url)

            if current_response.status_code == 200 and forecast_response.status_code == 200:
                current_data = current_response.json()
                forecast_data = forecast_response.json()

                weather_data = {
                    'city': current_data['name'],
                    'temp': current_data['main']['temp'],
                    'feels_like': current_data['main']['feels_like'],
                    'description': current_data['weather'][0]['description'],
                    'humidity': current_data['main']['humidity'],
                    'wind_speed': current_data['wind']['speed'],
                    'icon': current_data['weather'][0]['icon'],
                    'forecast': []
                }

                now = datetime.now()
                for item in forecast_data['list']:
                    forecast_time = datetime.fromtimestamp(item['dt'])
                    if forecast_time <= now + timedelta(hours=24):
                        weather_data['forecast'].append({
                            'time': forecast_time,
                            'temp': item['main']['temp'],
                            'icon': item['weather'][0]['icon'],
                            'description': item['weather'][0]['description'],
                            'humidity': item['main']['humidity'],
                            'wind': item['wind']['speed']
                        })

                if city not in history:
                    history = [city] + history
                    request.session['weather_search_history'] = history[:5]

            else:
                error = "Город не найден" if current_response.status_code == 404 else "Ошибка API"

        except Exception as e:
            error = f"Ошибка соединения: {str(e)}"

    return render(request, 'weather/home.html', {
        'weather': weather_data,
        'error': error,
        'history': history
    })


def city_autocomplete(request):
    query = request.GET.get('query', '')
    cache_key = f'autocomplete_{query}'
    cached = cache.get(cache_key)

    if cached is not None:
        return JsonResponse(cached, safe=False)

    if not query:
        return JsonResponse([])

    url = f"http://api.openweathermap.org/geo/1.0/direct?q={query}&limit=5&appid={settings.OPENWEATHER_API_KEY}"

    try:
        response = requests.get(url)
        suggestions = [{
            'name': f"{item['name']}, {item.get('country', '')}",
            'lat': item['lat'],
            'lon': item['lon']
        } for item in response.json()]

        cache.set(cache_key, suggestions, 60 * 60 * 6)
        return JsonResponse(suggestions, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)