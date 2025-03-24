from ..plugin_registry import PluginRegistry
from .jina_reader import JinaReaderPlugin
from .text_analyzer import TextAnalyzerPlugin
from .text_statistics import TextStatisticsPlugin
from .summarizer import SummarizerPlugin

def register_plugins():
    registry = PluginRegistry.get_instance()
    registry.register('jina-reader', JinaReaderPlugin)
    registry.register('text-analyzer', TextAnalyzerPlugin)
    registry.register('text-statistics', TextStatisticsPlugin)
    registry.register('summarizer', SummarizerPlugin)
