import importlib.metadata
import pathlib

import anywidget
import traitlets

try:
    __version__ = importlib.metadata.version("db_schema_viz")
except importlib.metadata.PackageNotFoundError:
    __version__ = "unknown"


class DBSchemaVizWidget(anywidget.AnyWidget):
    _esm = pathlib.Path(__file__).parent / "static" / "index.js"
    _css = pathlib.Path(__file__).parent / "static" / "index.css"
    value = traitlets.Int(0).tag(sync=True)
