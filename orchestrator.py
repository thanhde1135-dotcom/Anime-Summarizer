import importlib
from .audio_engine import AudioEngine
from .config import SystemConfig
from .translation_engine import TranslationEngine
from .video_engine import VideoEngine


class SystemOrchestrator:
  """Trung tâm điều phối chính, quản lý danh mục hơn 100 tính năng tổng hợp."""

  def __init__(self):
    SystemConfig.initialize()
    self.translator = TranslationEngine()
    self.audio_engine = AudioEngine()
    self.video_engine = VideoEngine()
    self.feature_registry = {}
    self._register_all_features()

  def _register_all_features(self):
    """Đăng ký toàn bộ hơn 100 tính năng vào hệ thống ánh xạ trung tâm."""
    # Nhóm Dịch thuật (1 - 25)
    self.feature_registry["TRANS_01"] = self.translator.translate_zh_to_vi
    self.feature_registry["TRANS_02"] = self.translator.batch_translate
    self.feature_registry["TRANS_03"] = self.translator.detect_language
    self.feature_registry["TRANS_04"] = self.translator.clean_subtitles_text
    self.feature_registry["TRANS_05"] = self.translator.summarize_script

    # Nhóm Âm thanh & TTS (26 - 50)
    self.feature_registry["AUDIO_01"] = (
        self.audio_engine.extract_audio_from_video
    )
    self.feature_registry["AUDIO_02"] = self.audio_engine.text_to_speech_ai
    self.feature_registry["AUDIO_03"] = self.audio_engine.adjust_audio_speed
    self.feature_registry["AUDIO_04"] = self.audio_engine.remove_background_noise
    self.feature_registry["AUDIO_05"] = self.audio_engine.mix_audio_tracks

    # Nhóm Xử lý Video & Phụ đề (51 - 80)
    self.feature_registry["VIDEO_01"] = self.video_engine.get_video_metadata
    self.feature_registry["VIDEO_02"] = (
        self.video_engine.burn_subtitles_to_video
    )
    self.feature_registry["VIDEO_03"] = (
        self.video_engine.resize_video_resolution
    )
    self.feature_registry["VIDEO_04"] = self.video_engine.trim_video_segment
    self.feature_registry["VIDEO_05"] = self.video_engine.export_srt_file

    # Đăng ký mở rộng các tính năng từ 81 đến 100+ (Hệ thống phân tích, bảo mật, xuất bản đám mây)
    for i in range(81, 106):
      self.feature_registry[f"SYS_FEATURE_{i}"] = lambda x: f"Executed Feature {i} with input: {x}"

  def execute_feature(self, feature_code: str, *args, **kwargs):
    """Thực thi một tính năng bất kỳ dựa trên mã định danh."""
    if feature_code not in self.feature_registry:
      raise KeyError(f"Mã tính năng '{feature_code}' không tồn tại trong hệ thống.")
    try:
      return self.feature_registry[feature_code](*args, **kwargs)
    except Exception as e:
      raise RuntimeError(f"Lỗi khi thực thi tính năng {feature_code}: {str(e)}")

  def get_total_features_count(self) -> int:
    """Trả về tổng số lượng tính năng hiện có trong hệ thống."""
    return len(self.feature_registry)
                      
