import redis

from model import Configuration

CONFIGURATION_PATH = "static/configuration.json"

db = redis.Redis(host='redis', port=6379, decode_responses=True)


class ConfigurationService:

    @staticmethod
    def get_configuration() -> list:
        config = db.lrange('malicious_words', 0, -1)
        return config

    @staticmethod
    def update_configuration(new_configuration: list[str]):
        new_configuration = Configuration(config=new_configuration)
        db.delete('malicious_words')
        if new_configuration.config:
            db.rpush('malicious_words', *new_configuration.config)
