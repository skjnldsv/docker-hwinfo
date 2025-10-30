from flask import Flask, Response
import socket, psutil, platform, datetime, os

app = Flask(__name__)

@app.route("/")
def info():
    vm = psutil.virtual_memory()
    uptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())

    # Get CPU model (Linux)
    cpu_model = "Unknown"
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if "model name" in line:
                    cpu_model = line.split(":", 1)[1].strip()
                    break
    except Exception:
        cpu_model = platform.processor() or "Unknown"

    host_name = os.getenv('NODE_HOSTNAME', socket.gethostname())
    text = (
        f"Node: {host_name}\n"
        f"Platform: {platform.platform()}\n"
        f"CPU model: {cpu_model}\n"
        f"CPU cores: {psutil.cpu_count(logical=False)}\n"
        f"CPU threads: {psutil.cpu_count()}\n"
        f"Memory total: {round(vm.total / 1e9, 2)} GB\n"
        f"Memory used: {round(vm.used / 1e9, 2)} GB ({vm.percent}%)\n"
        f"Uptime: {str(uptime).split('.')[0]}\n"
        f"Container hostname: {host_name}\n"
    )

    return Response(text, mimetype="text/plain")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
