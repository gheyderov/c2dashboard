from django.shortcuts import render, redirect
from django.http import JsonResponse
from subprocess import Popen
from server import HOST, PORT
from django.contrib import messages
import psutil

# Global variable
server_process = None


def start_server(request):
    global server_process
    if request.method == 'POST':
        try:
            global server_process
            # Start your server
            server_process = Popen(['python', 'server.py'])
            messages.success(request, f'Server listening on {HOST}:{PORT}')
        except Exception as e:
            messages.error(request, f'Error starting server: {e}')
    return render(request, 'index.html', {'server_process': server_process})


def stop_server(request):
    global server_process
    if server_process is not None:
        # Find the process associated with the server
        for proc in psutil.process_iter(['pid', 'name']):
            if 'python' in proc.info['name'] and 'server.py' in proc.cmdline():
                proc.terminate()
                server_process = None
                messages.success(request, 'Server stopped successfully')
                print('Server stopped successfully')
                break
        else:
            messages.error(request, 'Server process not found')
            print('Server process not found')
    else:
        messages.error(request, 'Server is not running')
        print('Server is not running')
    return redirect('start_server')
