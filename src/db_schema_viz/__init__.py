import pathlib

import anywidget
import traitlets


class DBSchemaVizWidget(anywidget.AnyWidget):
    _esm = pathlib.Path(__file__).parent / "static" / "index.js"
    _css = pathlib.Path(__file__).parent / "static" / "index.css"
    entities = traitlets.List(default_value=[]).tag(sync=True)
    width = traitlets.Int(default_value=1000).tag(sync=True)
    height = traitlets.Int(default_value=700).tag(sync=True)
