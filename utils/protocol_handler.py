"""
Protocol handler for browser integration
"""

import os
import sys
import threading
import socket
import json
from urllib.parse import unquote
import subprocess
from pathlib import Path

class ProtocolHandler:
    """Handles custom protocol for browser integration"""
    
    def __init__(self, protocol_name='mediaprocessor'):
        self.protocol_name = protocol_name
        self.callback = None
        self.server_socket = None
        self.server_thread = None
        self.running = False
        
        # Setup protocol handler
        try:
            self.setup_protocol_handler()
            self.start_server()
        except Exception as e:
            print(f"Warning: Could not setup protocol handler: {e}")
            
    def setup_protocol_handler(self):
        """Setup custom protocol handler in the system"""
        if sys.platform == "win32":
            self._setup_windows_protocol()
        elif sys.platform == "darwin":
            self._setup_macos_protocol()
        elif sys.platform.startswith("linux"):
            self._setup_linux_protocol()
            
    def _setup_windows_protocol(self):
        """Setup protocol handler on Windows"""
        try:
            import winreg
            
            # Get the path to the current executable
            exe_path = sys.executable
            if hasattr(sys, 'frozen'):
                exe_path = sys.executable
            else:
                exe_path = f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}"'
                
            # Create registry entries
            protocol_key = fr"SOFTWARE\Classes\{self.protocol_name}"
            
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, protocol_key) as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f"URL:{self.protocol_name} Protocol")
                winreg.SetValueEx(key, "URL Protocol", 0, winreg.REG_SZ, "")
                
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"{protocol_key}\\shell\\open\\command") as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f'{exe_path} --protocol-url "%1"')
                
        except ImportError:
            print("winreg not available, skipping Windows protocol handler setup")
        except Exception as e:
            print(f"Error setting up Windows protocol handler: {e}")
            
    def _setup_macos_protocol(self):
        """Setup protocol handler on macOS"""
        try:
            # Create a simple app bundle for protocol handling
            app_name = "MediaProcessor"
            app_path = Path.home() / "Applications" / f"{app_name}.app"
            
            if not app_path.exists():
                # Create basic app structure
                app_path.mkdir(parents=True, exist_ok=True)
                contents_path = app_path / "Contents"
                contents_path.mkdir(exist_ok=True)
                
                # Create Info.plist
                info_plist = contents_path / "Info.plist"
                plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleIdentifier</key>
    <string>com.mediaprocessor.app</string>
    <key>CFBundleName</key>
    <string>{app_name}</string>
    <key>CFBundleURLTypes</key>
    <array>
        <dict>
            <key>CFBundleURLName</key>
            <string>{self.protocol_name} URL</string>
            <key>CFBundleURLSchemes</key>
            <array>
                <string>{self.protocol_name}</string>
            </array>
        </dict>
    </array>
</dict>
</plist>"""
                
                with open(info_plist, 'w') as f:
                    f.write(plist_content)
                    
        except Exception as e:
            print(f"Error setting up macOS protocol handler: {e}")
            
    def _setup_linux_protocol(self):
        """Setup protocol handler on Linux"""
        try:
            # Create .desktop file
            desktop_dir = Path.home() / ".local" / "share" / "applications"
            desktop_dir.mkdir(parents=True, exist_ok=True)
            
            desktop_file = desktop_dir / "mediaprocessor.desktop"
            
            exe_path = sys.executable
            if not hasattr(sys, 'frozen'):
                exe_path = f'{sys.executable} {os.path.abspath(sys.argv[0])}'
                
            desktop_content = f"""[Desktop Entry]
Name=Media Processor
Exec={exe_path} --protocol-url %u
Type=Application
MimeType=x-scheme-handler/{self.protocol_name};
"""
            
            with open(desktop_file, 'w') as f:
                f.write(desktop_content)
                
            # Make executable
            os.chmod(desktop_file, 0o755)
            
            # Register the protocol
            try:
                subprocess.run(['xdg-mime', 'default', 'mediaprocessor.desktop', f'x-scheme-handler/{self.protocol_name}'], 
                             check=False)
            except FileNotFoundError:
                pass  # xdg-mime not available
                
        except Exception as e:
            print(f"Error setting up Linux protocol handler: {e}")
            
    def start_server(self):
        """Start local server for protocol handling"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('localhost', 0))  # Use any available port
            self.server_socket.listen(5)
            
            self.port = self.server_socket.getsockname()[1]
            self.running = True
            
            # Start server thread
            self.server_thread = threading.Thread(target=self._server_loop, daemon=True)
            self.server_thread.start()
            
        except Exception as e:
            print(f"Error starting protocol server: {e}")
            
    def _server_loop(self):
        """Main server loop for handling protocol requests"""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                
                # Handle request in separate thread
                request_thread = threading.Thread(
                    target=self._handle_request, 
                    args=(client_socket,), 
                    daemon=True
                )
                request_thread.start()
                
            except Exception as e:
                if self.running:
                    print(f"Error in protocol server: {e}")
                break
                
    def _handle_request(self, client_socket):
        """Handle individual protocol request"""
        try:
            # Read request
            data = client_socket.recv(1024).decode('utf-8')
            
            # Parse the URL from the request
            if data.startswith('GET /'):
                path = data.split(' ')[1]
                if path.startswith('/url/'):
                    url = unquote(path[5:])  # Remove '/url/' prefix
                    
                    # Call callback with the URL
                    if self.callback:
                        self.callback(url)
                        
            # Send response
            response = "HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nOK"
            client_socket.send(response.encode('utf-8'))
            
        except Exception as e:
            print(f"Error handling protocol request: {e}")
        finally:
            client_socket.close()
            
    def set_callback(self, callback):
        """Set callback function for handling protocol URLs"""
        self.callback = callback
        
    def handle_protocol_url(self, url):
        """Handle protocol URL directly (for command line usage)"""
        if url and url.startswith(f'{self.protocol_name}://'):
            # Extract the actual URL
            actual_url = url[len(f'{self.protocol_name}://'):]
            if self.callback:
                self.callback(actual_url)
                
    def stop(self):
        """Stop the protocol handler server"""
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
                
    def get_protocol_url(self, url):
        """Get the protocol URL for a given URL"""
        return f"{self.protocol_name}://localhost:{self.port}/url/{url}"

# Handle command line protocol URLs
if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--protocol-url":
        protocol_url = sys.argv[2]
        
        # Extract actual URL
        if protocol_url.startswith('mediaprocessor://'):
            actual_url = protocol_url[17:]  # Remove 'mediaprocessor://'
            
            # Send to running instance via socket
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(('localhost', 23456))  # Default port
                sock.send(f"GET /url/{actual_url} HTTP/1.1\r\n\r\n".encode('utf-8'))
                sock.close()
            except:
                # If no running instance, start the application
                os.system(f'python "{os.path.dirname(__file__)}/../main.py"')
