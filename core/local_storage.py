import json
from pathlib import Path
from typing import Dict, List
from core.models import DataBase, ExportScript, DataBaseType

class LocalStorage:
    def __init__(self, file_path: str = "config.json"):
        self.file_path = Path(file_path)
        self.data_sources: Dict[str, DataBase] = {}
        self.scripts: Dict[str, ExportScript] = {}
        self.load()

    def load(self):
        if self.file_path.exists():
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for ds in data.get('data_sources', []):
                    self.data_sources[ds['name']] = DataBase(
                        name=ds['name'],
                        type=DataBaseType(ds['type']),
                        host=ds['host'],
                        port=ds['port'],
                        username=ds.get('username', ''),
                        password=ds.get('password', ''),
                        database=ds.get('database', '')
                    )
                for script in data.get('scripts', []):
                    self.scripts[script['name']] = ExportScript(
                        name=script['name'],
                        fields=script['fields'],
                        sql=script['sql'],
                        data_source_name=script.get('data_source_name', '')
                    )

    def save(self):
        data = {
            'data_sources': [
                {
                    'name': ds.name,
                    'type': ds.type.value,
                    'host': ds.host,
                    'port': ds.port,
                    'username': ds.username,
                    'password': ds.password,
                    'database': ds.database
                } for ds in self.data_sources.values()
            ],
            'scripts': [
                {
                    'name': script.name,
                    'fields': script.fields,
                    'sql': script.sql,
                    'data_source_name': script.data_source_name
                } for script in self.scripts.values()
            ]
        }
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)