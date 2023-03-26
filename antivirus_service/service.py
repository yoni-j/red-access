import os
import uuid
import redis
import requests
import logging
from rq import Queue

CONFIGURATION_SERVICE_URL = 'http://config-service:8000/'
logger = logging.getLogger(__name__)

MALICIOUS_WORDS_KEY = 'av_malicious_words'
JOBS_KEY = 'jobs'


class JobStatus:
    IN_PROGRESS = "in_progress"
    DETECTED = "detected"
    CLEAN = "clean"
    FAILED = "failed"


def dequeue_scan(filename):
    redis_conn = redis.Redis(host='redis', port=6379, decode_responses=True)
    job_antivirus_service = AntivirusService(redis_conn)
    job_antivirus_service.scan(filename)


class AntivirusService:
    def __init__(self, redis_conn):
        self.redis_conn = redis_conn
        self.scan_queue = Queue(connection=self.redis_conn)

    def fetch_config(self):
        try:
            res = requests.get(CONFIGURATION_SERVICE_URL)
            if res.status_code == 200:
                words = res.json()
                if words:
                    self.redis_conn.delete(MALICIOUS_WORDS_KEY)
                    self.redis_conn.lpush(MALICIOUS_WORDS_KEY, *words)
        except Exception as e:
            print('Failed to fetch config:', e)

    def scan(self, filename):
        file_path = self.get_file_path(filename)
        with open(file_path, "rb") as file:
            content = file.read().decode('utf-8', errors='ignore')
            job_id = filename.split(".")[0]
            for word in self.get_config():
                if word in content:
                    self.redis_conn.hset(JOBS_KEY, job_id, JobStatus.DETECTED)
                    return
            self.redis_conn.hset(JOBS_KEY, job_id, JobStatus.CLEAN)

    def create_scan_job(self, file):
        extension = file.filename.split(".")[-1]
        job_id = str(uuid.uuid4())
        new_file_name = f"{job_id}.{extension}"
        file_path = self.get_file_path(new_file_name)
        file.save(file_path)
        self.scan_queue.enqueue(dequeue_scan, new_file_name)
        self.redis_conn.hset(JOBS_KEY, job_id, JobStatus.IN_PROGRESS)
        return job_id

    def get_config(self):
        return self.redis_conn.lrange(MALICIOUS_WORDS_KEY, 0, -1) or []

    def get_job_status(self, job_id):
        return self.redis_conn.hget(JOBS_KEY, job_id)

    @staticmethod
    def get_file_path(filename):
        scans_folder_path = '/to_scan'
        os.makedirs(scans_folder_path, exist_ok=True)
        return os.path.join(scans_folder_path, filename)
