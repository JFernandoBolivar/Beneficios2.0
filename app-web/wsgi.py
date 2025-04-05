from app import app
from waitress import serve
import os
from pathlib import Path
import socket

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return '127.0.0.1'

def create_server_info_file(port, local_ip):
    try:
        # Get desktop path
        desktop_path = os.path.join(Path.home(), 'Desktop')
        file_path = os.path.join(desktop_path, 'server_info.txt')
        
        # Create the content
        content = f"""
={'='*48}=
Production server running on:
Local URL: http://localhost:{port}
Network URL: http://{local_ip}:{port}
={'='*48}=
"""
        
        # Write to file
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"Server information written to: {file_path}")
    except Exception as e:
        print(f"Error writing server info file: {str(e)}")

if __name__ == "__main__":
    host = '0.0.0.0'
    port = 8000
    local_ip = get_local_ip()
    print('\n' + '='*50)
    print(f'Production server running on:')
    print(f'Local URL: http://localhost:{port}')
    print(f'Network URL: http://{local_ip}:{port}')
    print('='*50 + '\n')
    
    # Create server info file on desktop
    create_server_info_file(port, local_ip)
    # Optimized settings for network performance
    serve(
    app,
    host=host,
    port=port,
    threads=16,                    # Aumentado de 8 a 16
    connection_limit=1000,
    channel_timeout=120,           # Reducido de 300 a 120
    cleanup_interval=30,
    url_scheme='https',
    ident='Flask-Production',
    outbuf_overflow=2097152,       # Aumentado a 2MB
    inbuf_overflow=2097152         # Aumentado a 2MB
)
