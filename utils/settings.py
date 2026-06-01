import json
import os

class AppSettings:
    """应用设置持久化"""
    
    def __init__(self, config_dir: str = None):
        if config_dir is None:
            config_dir = os.path.expanduser("~/.pdf-tool")
        os.makedirs(config_dir, exist_ok=True)
        self.config_path = os.path.join(config_dir, "settings.json")
        self._data = self._load()
    
    def _load(self) -> dict:
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    return json.load(f)
            except:
                pass
        return {
            "output_dir": os.path.expanduser("~/Documents/PDF_输出/"),
            "theme": "light",
            "recent_files": [],
            "batch_concurrency": 2,
            "default_page_size": "A4",
            "default_orientation": "portrait",
        }
    
    def save(self):
        with open(self.config_path, "w") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)
    
    def get(self, key: str, default=None):
        return self._data.get(key, default)
    
    def set(self, key: str, value):
        self._data[key] = value
        self.save()
    
    def add_recent(self, file_path: str, action: str):
        """添加最近文件记录"""
        recent = self._data.get("recent_files", [])
        recent.insert(0, {
            "path": file_path,
            "action": action,
            "time": __import__("datetime").datetime.now().isoformat(),
        })
        if len(recent) > 50:
            recent = recent[:50]
        self._data["recent_files"] = recent
        self.save()
