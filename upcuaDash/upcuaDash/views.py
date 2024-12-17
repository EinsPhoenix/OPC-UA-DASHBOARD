from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .upcuaclient import opc_client
from django.shortcuts import render

def get_sensor_data(request):
    """API to fetch current sensor data."""
    return JsonResponse(opc_client.data)

@csrf_exempt
def set_fan_speed(request):
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


def dashboard_view(request):
    return render(request, "dashboard.html")