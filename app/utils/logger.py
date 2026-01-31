"""
Story Producer Logger - Detaylı loglama sistemi
Her hikaye üretimi için ayrı log dosyası + genel özet log
"""

import os
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import time

class StoryLogger:
    """Hikaye üretim sürecini loglar."""
    
    def __init__(self, logs_dir: str = "logs"):
        self.logs_dir = logs_dir
        self._ensure_logs_dir()
        
        # Ana logger ayarları
        self.logger = logging.getLogger("StoryProducer")
        self.logger.setLevel(logging.DEBUG)
        
        # Dosya handler - genel log (konsol yok - cloud için temiz)
        file_handler = logging.FileHandler(
            os.path.join(self.logs_dir, "story_producer.log"),
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
        file_handler.setFormatter(file_format)
        
        # Handler'ı ekle (eğer yoksa)
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
        
        # Mevcut işlem için veriler
        self.current_session: Optional[Dict[str, Any]] = None
        self.step_times: Dict[str, float] = {}
    
    def _ensure_logs_dir(self):
        """Log klasörünün var olduğundan emin ol."""
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)
        
        # Sessions klasörü
        sessions_dir = os.path.join(self.logs_dir, "sessions")
        if not os.path.exists(sessions_dir):
            os.makedirs(sessions_dir)
    
    def start_session(self, book_name: str, length: str, style: str) -> str:
        """Yeni bir hikaye üretim oturumu başlat."""
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        self.current_session = {
            "session_id": session_id,
            "book_name": book_name,
            "settings": {
                "length": length,
                "style": style
            },
            "started_at": datetime.now().isoformat(),
            "steps": [],
            "metrics": {},
            "errors": [],
            "status": "started"
        }
        
        self.step_times = {}
        self.logger.info(f"🚀 Yeni oturum başladı: {session_id} | Kitap: {book_name}")
        
        return session_id
    
    def log_step(self, step_name: str, details: Dict[str, Any] = None):
        """Bir adımı logla."""
        if not self.current_session:
            return
        
        timestamp = time.time()
        
        step_data = {
            "name": step_name,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        
        # Önceki adımdan geçen süre
        if self.step_times:
            last_step = list(self.step_times.keys())[-1]
            duration = timestamp - self.step_times[last_step]
            step_data["duration_seconds"] = round(duration, 3)
        
        self.step_times[step_name] = timestamp
        self.current_session["steps"].append(step_data)
        
        # Konsola log
        details_str = ""
        if details:
            details_str = " | " + " | ".join([f"{k}: {v}" for k, v in details.items()])
        self.logger.info(f"📍 {step_name}{details_str}")
    
    def log_metric(self, name: str, value: Any):
        """Metrik kaydet."""
        if not self.current_session:
            return
        
        self.current_session["metrics"][name] = value
        self.logger.debug(f"📊 Metrik: {name} = {value}")
    
    def log_text_stats(self, original_size: int, cleaned_size: int):
        """Metin istatistiklerini logla."""
        removed = original_size - cleaned_size
        removed_percent = (removed / original_size * 100) if original_size > 0 else 0
        
        self.log_metric("original_text_size", original_size)
        self.log_metric("cleaned_text_size", cleaned_size)
        self.log_metric("removed_characters", removed)
        self.log_metric("removed_percent", round(removed_percent, 2))
        
        self.logger.info(f"📝 Metin: {original_size:,} -> {cleaned_size:,} ({removed_percent:.1f}% kaldırıldı)")
    
    def log_sampling(self, num_samples: int, sample_size: int, total_analyzed: int):
        """Örnekleme bilgilerini logla."""
        self.log_metric("num_samples", num_samples)
        self.log_metric("sample_size", sample_size)
        self.log_metric("total_analyzed_chars", total_analyzed)
        
        self.logger.info(f"🔬 Örnekleme: {num_samples} örnek × {sample_size//1000}KB = {total_analyzed//1000}KB")
    
    def log_analysis_results(self, analysis: Dict[str, Any]):
        """Analiz sonuçlarını logla."""
        if not analysis:
            return
        
        results = {
            "characters_found": len(analysis.get("characters", {})),
            "keywords_found": len(analysis.get("keywords", [])),
            "mood_words_found": len(analysis.get("mood_words", {})),
            "sentiment_polarity": analysis.get("sentiments", {}).get("polarity"),
            "sentiment_subjectivity": analysis.get("sentiments", {}).get("subjectivity")
        }
        
        self.log_metric("analysis_results", results)
        
        self.logger.info(f"🎭 Analiz: {results['characters_found']} karakter, {results['keywords_found']} anahtar kelime")
    
    def log_story_generated(self, story_length: int):
        """Hikaye üretildiğini logla."""
        word_count = len(story_length.split()) if isinstance(story_length, str) else story_length
        
        self.log_metric("story_word_count", word_count)
        self.logger.info(f"✍️ Hikaye üretildi: ~{word_count} kelime")
    
    def log_error(self, error: str, step: str = None):
        """Hata logla."""
        if self.current_session:
            self.current_session["errors"].append({
                "step": step,
                "error": str(error),
                "timestamp": datetime.now().isoformat()
            })
        
        self.logger.error(f"❌ Hata{f' ({step})' if step else ''}: {error}")
    
    def log_cache_hit(self, book_name: str):
        """Cache hit logla."""
        self.log_metric("cache_hit", True)
        self.logger.info(f"⚡ Cache hit: {book_name}")
    
    def end_session(self, success: bool = True):
        """Oturumu sonlandır ve kaydet."""
        if not self.current_session:
            return
        
        # Toplam süre hesapla
        if self.step_times:
            first_step = list(self.step_times.values())[0]
            last_step = list(self.step_times.values())[-1]
            total_duration = last_step - first_step
            self.current_session["total_duration_seconds"] = round(total_duration, 3)
        
        self.current_session["ended_at"] = datetime.now().isoformat()
        self.current_session["status"] = "success" if success else "failed"
        
        # Session dosyasına kaydet
        session_file = os.path.join(
            self.logs_dir, 
            "sessions", 
            f"{self.current_session['session_id']}_{self.current_session['book_name'].replace('.txt', '').replace(' ', '_')}.json"
        )
        
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(self.current_session, f, ensure_ascii=False, indent=2)
        
        # Özet log
        duration = self.current_session.get("total_duration_seconds", 0)
        status_emoji = "✅" if success else "❌"
        self.logger.info(f"{status_emoji} Oturum tamamlandı: {duration:.2f}s | Dosya: {session_file}")
        
        # Özet dosyasına ekle
        self._append_to_summary()
        
        self.current_session = None
        self.step_times = {}
    
    def _append_to_summary(self):
        """Özet log dosyasına ekle."""
        if not self.current_session:
            return
        
        summary_file = os.path.join(self.logs_dir, "summary.jsonl")
        
        summary_entry = {
            "session_id": self.current_session["session_id"],
            "book_name": self.current_session["book_name"],
            "status": self.current_session["status"],
            "duration_seconds": self.current_session.get("total_duration_seconds", 0),
            "timestamp": self.current_session["started_at"],
            "metrics": self.current_session.get("metrics", {})
        }
        
        with open(summary_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(summary_entry, ensure_ascii=False) + "\n")


# Global logger instance
story_logger = StoryLogger()
