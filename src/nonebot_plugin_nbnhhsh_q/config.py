from pydantic import BaseModel


class Config(BaseModel):
    """Plugin Config Here"""

    cache_clear_interval: int = 3600  # 缓存清理间隔，单位秒
