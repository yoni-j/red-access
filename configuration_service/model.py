from pydantic import BaseModel


class Configuration(BaseModel):
    config: list[str]
