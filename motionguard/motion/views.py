import cv2
import numpy as np
import qrcode
import socket
from io import BytesIO
from django.shortcuts import render, redirect
from django.http import StreamingHttpResponse, HttpResponse, JsonResponse
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

# ----------------------
# GLOBAL STATE
# ----------------------

latest_frame = None
background = None
camera_running = False  # start as False
VIDEO_URL = 0

# ----------------------
# CAMERA CONTROL VIEWS
# ----------------------


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

@csrf_exempt
@login_required
def start_camera(request):
    if request.method == 'POST':
        global camera_running
        if not camera_running:
            camera_running = True
            return JsonResponse({"status": "started"})
        else:
            return JsonResponse({"status": "already_running"})
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
@login_required
def stop_camera(request):
    if request.method == 'POST':
        global camera_running
        if camera_running:
            camera_running = False
            return JsonResponse({"status": "stopped"})
        else:
            return JsonResponse({"status": "already_stopped"})
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required
def camera_status(request):
    global camera_running
    return JsonResponse({"running": camera_running})

# ----------------------
# AUTHENTICATION VIEWS
# ----------------------

class CustomLoginView(LoginView):
    template_name = 'motion/login.html'

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

# ----------------------
# DASHBOARD & STREAM
# ----------------------

@login_required
def dashboard(request):
    return render(request, 'motion/dashboard.html')

@login_required
def phone_camera(request):
    return render(request, 'motion/camera.html')

@login_required
def video_feed(request):
    def generate():
        global latest_frame
        while True:
            if latest_frame:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + latest_frame + b'\r\n')
    return StreamingHttpResponse(generate(), content_type='multipart/x-mixed-replace; boundary=frame')

# ----------------------
# RECEIVE FRAMES FROM JS
# ----------------------

@csrf_exempt
@login_required
def receive_frame(request):
    global latest_frame
    if request.method == 'POST' and request.FILES.get('frame'):
        file = request.FILES['frame']
        data = np.frombuffer(file.read(), np.uint8)
        frame = cv2.imdecode(data, cv2.IMREAD_COLOR)

        processed = detect_motion(frame)
        _, jpeg = cv2.imencode('.jpg', processed)
        latest_frame = jpeg.tobytes()

        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'bad request'}, status=400)

# ----------------------
# MOTION DETECTION
# ----------------------

def detect_motion(frame):
    global background
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    if background is None:
        background = gray
        return frame

    diff = cv2.absdiff(background, gray)
    thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    motion = False
    for contour in contours:
        if cv2.contourArea(contour) < 1000:
            continue
        (x, y, w, h) = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
        motion = True

    if motion:
        cv2.putText(frame, "Motion Detected", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    return frame

# ----------------------
# QR PAIRING VIEW
# ----------------------

@login_required
def remote_camera_qr(request):
    host = request.get_host()
    url = f"http://{host}/cam/"
    qr = qrcode.make(url)
    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    return HttpResponse(buffer.getvalue(), content_type="image/png")
