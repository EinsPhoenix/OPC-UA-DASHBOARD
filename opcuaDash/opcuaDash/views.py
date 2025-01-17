from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .opcuaclient import opc_client
from django.shortcuts import render
import requests
from dotenv import load_dotenv
import os
import certifi
import logging
from datetime import datetime
from django.db.models import Q
from .models import EnergyData
import psutil
import random


logger = logging.getLogger(__name__)
async def get_sensor_data(request):
    """API to fetch current sensor data."""
    return JsonResponse(opc_client.data)

async def get_weather_data(latitude, longitude):
    """Helper function to fetch weather data from Visual Crossing API"""
    load_dotenv()
    api_key = os.getenv("WEATHER_API_KEY")
    
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{latitude},{longitude}?key={api_key}"
    
    session = requests.Session()
    session.verify = certifi.where()
    
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        
        if response.headers.get('Content-Type') == 'application/json':
            return response.json()
        else:
            logger.error(f"Unexpected content type: {response.headers.get('Content-Type')}")
            logger.error(f"Response content: {response.text}")
            return None
            
    except requests.exceptions.SSLError as e:
        logger.error(f"SSL Error: {str(e)}")
        raise Exception('SSL certificate verification failed')
    except requests.exceptions.Timeout:
        logger.error("Request timed out")
        raise Exception('Weather API request timed out')
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {str(e)}")
        raise Exception('Failed to fetch weather data')
    
    
    
    
    
logger = logging.getLogger(__name__)
async def energy_consumption(request):
    max_power_drain = 120
    base_consumption = 30
    cpu_usage = psutil.cpu_percent(interval=1)

    
    memory = psutil.virtual_memory()
    memory_usage = memory.percent

    # Its difficult to calculate the power usage this is onloy an estimation and depents
    estimated_power_watt = (max_power_drain * (cpu_usage / 100) * (memory_usage / 100))+base_consumption
    
    print(cpu_usage, estimated_power_watt, memory_usage)
    
    return JsonResponse(estimated_power_watt, safe=False)
    
def get_energy_data(request):
    """
    Helper function to fetch energy data from database.
    If no data is found, fetches from external API and stores in database.
    """
    try:
        starttime = int(request.GET.get("starttime", 0))  
    except ValueError:
        logger.error("Invalid starttime parameter provided")
        return JsonResponse({
            "error": "Invalid starttime parameter",
            "details": "The starttime parameter must be a valid integer"
        }, status=400)

    try:
        
        existing_data = EnergyData.objects.filter(
            Q(start_timestamp=starttime) | 
            Q(start_timestamp__lte=starttime, end_timestamp__gte=starttime)
        )
        
        if existing_data.exists():
           
            data = existing_data.values(
                'start_timestamp',
                'end_timestamp',
                'marketprice',
                'unit'
            )
            logger.info(f"Found {existing_data.count()} matching records in database")
            return JsonResponse({
                "message": "Data found in the database.",
                "count": existing_data.count(),
                "data": list(data)
            }, status=200)
        
        
        now = datetime.utcnow()
        timestamp_in_seconds = int(now.timestamp())
        timestamp_in_milliseconds = timestamp_in_seconds * 1000

        url = f"https://api.awattar.de/v1/marketdata?start={timestamp_in_milliseconds}"
        session = requests.Session()
        session.verify = certifi.where()

        try:
            response = session.get(url, timeout=10)
            response.raise_for_status()
            energy_data = response.json()

           
            EnergyData.objects.all().delete()  
            for item in energy_data.get("data", []):
                EnergyData.objects.create(
                    start_timestamp=item["start_timestamp"],
                    end_timestamp=item["end_timestamp"],
                    marketprice=item["marketprice"],
                    unit=item["unit"]
                )

            logger.info("Database updated with new energy data from API")
            return JsonResponse({
                "message": "Data fetched from API and stored in database.",
                "data": energy_data
            }, status=200)

        except requests.exceptions.SSLError as e:
            logger.error(f"SSL Error: {str(e)}")
            return JsonResponse({
                "error": "SSL certificate verification failed"
            }, status=500)
        except requests.exceptions.Timeout:
            logger.error("Request timed out")
            return JsonResponse({
                "error": "Request timed out"
            }, status=500)
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            return JsonResponse({
                "error": "Failed to fetch energy data"
            }, status=500)

    except Exception as e:
        logger.error(f"Error while processing request: {str(e)}")
        return JsonResponse({
            "error": "Internal server error",
            "details": str(e)
        }, status=500)

async def set_location(request):
    """Main handler for setting location and getting weather data"""
    if request.method != 'POST':
        return JsonResponse(
            {'status': 'error', 'message': 'Invalid request method.'}, 
            status=405
        )

    try:
       
        data = json.loads(request.body)
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        if not all([latitude, longitude]):
            return JsonResponse(
                {'status': 'error', 'message': 'Missing latitude or longitude'}, 
                status=400
            )

     
        weather_data = await get_weather_data(latitude, longitude)
        
        if weather_data is None:
            return JsonResponse(
                {'status': 'error', 'message': 'Failed to process weather data'}, 
                status=500
            )

        print("Succes")
        return JsonResponse({
            'status': 'success',
            'message': 'Location set successfully',
            'weather_data': weather_data
        })

    except Exception as e:
        return JsonResponse(
            {'status': 'error', 'message': str(e)}, 
            status=500
        )
    
@csrf_exempt
async def set_fan_speed(request):
    """API to set the fan speed."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            value = data.get("fan_speed")
            if value is not None:
                opc_client.set_fan_speed(value)
                return JsonResponse({"status": "success", "message": f"Fan speed set to {value}"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
    return JsonResponse({"status": "error", "message": "Invalid request"})


async def dashboard_view(request):
    return render(request, "dashboard.html")


async def load_request(request):
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    memory_usage = memory.percent
    combined_usage = (cpu_usage + memory_usage) / 2
    
    return JsonResponse({"status": "success", "result": {
            "current_load": combined_usage
        }})




async def random_sentence(request):
    file_path = os.path.join(os.path.dirname(__file__), '../popup.json')
    
    try:
       
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
       
        quotes = [item["text"] for item in data["quote"]]
        
       
        random_quote = random.choice(quotes)
        
        return JsonResponse({"quote": random_quote}, safe=False)
    except FileNotFoundError:
        return JsonResponse({"error": "Die Datei 'popup.json' wurde nicht gefunden."}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Fehler beim Lesen der JSON-Datei."}, status=500)
   