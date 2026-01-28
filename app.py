from flask import Flask
import psutil
import platform
import socket
import os
from datetime import timedelta
import subprocess

app = Flask(__name__)

def get_memory_info():
    """Get detailed memory information including model and brand"""
    memory_info = {
        'model': 'Unknown',
        'brand': 'Unknown',
        'speed': 'Unknown'
    }
    
    try:
        # Try to get memory info from dmidecode
        result = subprocess.run(
            ['dmidecode', '-t', 'memory'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            output = result.stdout
            current_module = {}
            
            for line in output.split('\n'):
                line = line.strip()
                
                # Look for memory device sections
                if 'Memory Device' in line and current_module:
                    # Process previous module if it had data
                    if current_module.get('size') and current_module['size'] != 'No Module Installed':
                        if memory_info['model'] == 'Unknown' and current_module.get('part_number'):
                            memory_info['model'] = current_module['part_number']
                        if memory_info['brand'] == 'Unknown' and current_module.get('manufacturer'):
                            memory_info['brand'] = current_module['manufacturer']
                        if memory_info['speed'] == 'Unknown' and current_module.get('speed'):
                            memory_info['speed'] = current_module['speed']
                    current_module = {}
                
                # Parse memory attributes
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key == 'Manufacturer':
                        current_module['manufacturer'] = value
                    elif key == 'Part Number':
                        current_module['part_number'] = value
                    elif key == 'Size':
                        current_module['size'] = value
                    elif key == 'Speed':
                        current_module['speed'] = value
            
            # Process last module
            if current_module.get('size') and current_module['size'] != 'No Module Installed':
                if memory_info['model'] == 'Unknown' and current_module.get('part_number'):
                    memory_info['model'] = current_module['part_number']
                if memory_info['brand'] == 'Unknown' and current_module.get('manufacturer'):
                    memory_info['brand'] = current_module['manufacturer']
                if memory_info['speed'] == 'Unknown' and current_module.get('speed'):
                    memory_info['speed'] = current_module['speed']
    
    except Exception as e:
        print(f"Could not get detailed memory info: {e}")
    
    return memory_info

def get_cpu_model():
    """Get CPU model name"""
    try:
        if platform.system() == "Linux":
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if 'model name' in line:
                        return line.split(':')[1].strip()
    except:
        pass
    return platform.processor() or "Unknown"

@app.route('/')
def home():
    # Get system information
    cpu_model = get_cpu_model()
    cpu_cores = psutil.cpu_count(logical=False)
    cpu_threads = psutil.cpu_count(logical=True)
    
    # Memory information
    memory = psutil.virtual_memory()
    memory_total = memory.total / (1024 ** 3)  # Convert to GB
    memory_used = memory.used / (1024 ** 3)
    memory_percent = memory.percent
    
    # Get detailed memory info
    memory_details = get_memory_info()
    
    # Uptime
    boot_time = psutil.boot_time()
    uptime_seconds = psutil.time.time() - boot_time
    uptime = str(timedelta(seconds=int(uptime_seconds)))
    
    # Node and container info
    node_name = os.environ.get('NODE_HOSTNAME', socket.gethostname())
    container_hostname = socket.gethostname()
    
    # Build the output
    output = f"""Node: {node_name}
Platform: {platform.platform()}
CPU model: {cpu_model}
CPU cores: {cpu_cores}
CPU threads: {cpu_threads}
Memory total: {memory_total:.2f} GB
Memory used: {memory_used:.2f} GB ({memory_percent:.0f}%)
Memory brand: {memory_details['brand']}
Memory model: {memory_details['model']}
Memory speed: {memory_details['speed']}
Uptime: {uptime}
Container hostname: {container_hostname}
"""
    
    return output, 200, {'Content-Type': 'text/plain; charset=utf-8'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
