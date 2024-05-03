from django.shortcuts import render, redirect
from subprocess import Popen
from server import HOST, PORT, load_clients, remove_all_clients
from django.contrib import messages
from django.core.cache import cache
import psutil

# Global variable
server_process = None


def start_server(request):
    global server_process
    clients = load_clients()
    formatted_clients = {
        client_id: {
            "address": clients[client_id]["address"],
            "username": clients[client_id]["username"],
            "os": clients[client_id]["os"]
        }
        for client_id in clients
    }
    connected_agents = formatted_clients  # Get the list of connected clients
    if request.method == 'POST':
        try:
            global server_process
            # Start your server
            server_process = Popen(['python', 'server.py'])
            messages.success(request, f'Server listening on {HOST}:{PORT}')
        except Exception as e:
            messages.error(request, f'Error starting server: {e}')
    context = {
        'connected_agents': connected_agents,
        'server_process': server_process
    }
    return render(request, 'index.html', context)


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
            server_process = None
            messages.error(request, 'Server process not found')
            print('Server process not found')
    else:
        server_process = None
        messages.error(request, 'Server is not running')
        print('Server is not running')
    cache.set('command_responses', {})
    remove_all_clients()
    return redirect('start_server')


def send_command(request):
    if request.method == 'POST':
        command = request.POST.get('command', '')
        print("Send Command:", command)
        if not command:
            messages.error(request, 'Command cannot be empty')
            return redirect('start_server')
        else:
            cache.set('command', command)

    return redirect('start_server')
