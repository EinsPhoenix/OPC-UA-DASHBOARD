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
