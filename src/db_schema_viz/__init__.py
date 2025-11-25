import pathlib

import anywidget
import traitlets


class DBSchemaVizWidget(anywidget.AnyWidget):
    _esm = pathlib.Path(__file__).parent / "static" / "index.js"
    _css = pathlib.Path(__file__).parent / "static" / "index.css"
    entities = traitlets.Dict(default_value={}).tag(sync=True)
    width = traitlets.Int(default_value=0).tag(sync=True)  # 0 means auto (fit parent)
    height = traitlets.Int(default_value=700).tag(sync=True)
    show_datatypes = traitlets.Bool(default_value=True).tag(sync=True)
    datatype_truncate_length = traitlets.Int(default_value=30).tag(sync=True)
