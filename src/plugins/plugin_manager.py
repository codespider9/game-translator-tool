import importlib
from pathlib import Path
from typing import Dict, List
from src.plugins.base_plugin import BaseParserPlugin


class PluginManager:
    """Dynamically discovers and loads external game engine parser plugins."""

    def __init__(self, plugins_dir: str = None):
        if plugins_dir is None:
            plugins_dir = Path(__file__).parent
        else:
            plugins_dir = Path(plugins_dir)

        self.plugins_dir = plugins_dir
        self.loaded_plugins: Dict[str, BaseParserPlugin] = {}

    def discover_and_load(self) -> Dict[str, BaseParserPlugin]:
        """Scans plugins directory and instantiates valid parser plugins."""
        for file_path in self.plugins_dir.glob("*.py"):
            if file_path.name in ["__init__.py", "base_plugin.py", "plugin_manager.py"]:
                continue

            module_name = f"src.plugins.{file_path.stem}"
            try:
                module = importlib.import_module(module_name)
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (
                        isinstance(attr, type)
                        and issubclass(attr, BaseParserPlugin)
                        and attr is not BaseParserPlugin
                    ):
                        plugin_instance = attr()
                        self.loaded_plugins[plugin_instance.plugin_name] = plugin_instance
                        print(f"Loaded plugin: {plugin_instance.plugin_name}")
            except Exception as e:
                print(f"Failed to load plugin {file_path.name}: {e}")

        return self.loaded_plugins

    def get_plugin_names(self) -> List[str]:
        """Returns names of all active loaded plugins."""
        return list(self.loaded_plugins.keys())