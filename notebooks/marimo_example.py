import marimo

__generated_with = "0.18.0"
app = marimo.App(width="columns")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    TODO: figure out how to make 'hot reload' work during development (atm, only the Jupyter example works)
    """)
    return


@app.cell
def _(mo):
    from db_schema_viz import DBSchemaVizWidget

    widget = mo.ui.anywidget(DBSchemaVizWidget())
    widget
    return (widget,)


@app.cell
def _(widget):
    widget.value
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


if __name__ == "__main__":
    app.run()
