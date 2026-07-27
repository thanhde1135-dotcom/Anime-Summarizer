import os
from pathlib import Path


class SystemConfig:
  """Lớp quản lý cấu hình hệ thống toàn cục."""

  BASE_DIR = Path(__file__).resolve().parent
  TEMP_DIR = BASE_DIR / "temp"
  OUTPUT_DIR = BASE_DIR / "output"
  SUPPORTED_LANGUAGES = ["zh", "vi", "en", "ja", "ko", "es", "fr"]
  MAX_WORKERS = 4
  DEFAULT_FPS = 30

  @classmethod
  def initialize(cls):
    cls.TEMP_DIR.mkdir(parents=True, exist_ok=True)
    cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
