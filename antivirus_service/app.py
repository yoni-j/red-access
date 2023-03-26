import datetime

from flask import Flask, request
import redis
from service import AntivirusService
from rq import Queue

app = Flask(__name__)
redis_conn = redis.Redis(host='redis', port=6379, decode_responses=True)
queue = Queue(connection=redis_conn)
antivirus_service = AntivirusService(redis_conn)


@app.route('/scan', methods=['POST'])
def scan_file():
    file = request.files['file']
    return {"job_id": antivirus_service.create_scan_job(file)}


@app.route('/get_config', methods=['GET'])
def get_config():
    return antivirus_service.get_config()


@app.route('/scan_status/<job_id>', methods=['GET'])
def scan_status(job_id):
    return {"status": antivirus_service.get_job_status(job_id)}


def fetch_config():
    antivirus_service.fetch_config()


job = queue.enqueue_in(datetime.timedelta(seconds=60), fetch_config)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001)
