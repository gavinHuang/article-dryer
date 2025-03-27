from ..plugin_registry import PluginRegistry
from .jina_reader import JinaReaderPlugin
from .text_statistics import TextStatisticsPlugin
from .summarizer import SummarizerPlugin
from .word_level_analyzer import WordLevelAnalyzerPlugin

def register_plugins():
    registry = PluginRegistry.get_instance()
    registry.register('jina-reader', JinaReaderPlugin)
    registry.register('text-statistics', TextStatisticsPlugin)
    registry.register('summarizer', SummarizerPlugin)
    registry.register('word-level-analyzer', WordLevelAnalyzerPlugin)
