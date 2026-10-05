import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def line_chart(df, x_col, y_col, title, color_col=None, x_title=None, y_title=None):
    if df is None or df.empty:
        return go.Figure()
    if color_col:
        fig = px.line(df, x=x_col, y=y_col, color=color_col, title=title, markers=True)
    else:
        fig = px.line(df, x=x_col, y=y_col, title=title, markers=True)
    fig.update_layout(hovermode="x unified", template="plotly_white", legend_title_text="Commodity")
    if x_title:
        fig.update_xaxes(title_text=x_title)
    if y_title:
        fig.update_yaxes(title_text=y_title)
    return fig


def bar_chart(df, x_col, y_col, title, color_col=None):
    if df is None or df.empty:
        return go.Figure()
    if color_col:
        fig = px.bar(df, x=x_col, y=y_col, color=color_col, title=title)
    else:
        fig = px.bar(df, x=x_col, y=y_col, title=title)
    fig.update_layout(template="plotly_white", hovermode="x unified")
    return fig


def scatter_chart(df, x_col, y_col, color_col, title):
    if df is None or df.empty:
        return go.Figure()
    fig = px.scatter(df, x=x_col, y=y_col, color=color_col, title=title, trendline="ols")
    fig.update_layout(template="plotly_white")
    return fig


def sankey_chart(df, commodity=None):
    filtered = df.copy()
    if commodity and commodity != "All":
        filtered = filtered[filtered.get("Product", filtered.get("Commodity", pd.Series(["All"] * len(filtered)))) == commodity]

    if filtered.empty:
        return go.Figure()

    source_series = filtered["Location"].fillna("Unknown")
    collection = filtered["Collection_Centre"].fillna("Collection Centre")
    apmc = filtered["APMC_Market"].fillna("APMC Vashi")
    distributor = filtered["Distributor_Type"].fillna("Distributor")

    labels = list(dict.fromkeys(list(source_series) + list(collection) + list(apmc) + list(distributor)))
    lookup = {label: i for i, label in enumerate(labels)}

    source_idx = [lookup[v] for v in source_series]
    target_idx = [lookup[v] for v in collection]
    second_source = [lookup[v] for v in collection]
    second_target = [lookup[v] for v in apmc]
    third_source = [lookup[v] for v in apmc]
    third_target = [lookup[v] for v in distributor]

    all_source = source_idx + second_source + third_source
    all_target = target_idx + second_target + third_target
    all_value = list(filtered["Quantity_Produced_kg"].fillna(0).astype(float)) + list(filtered["Quantity_Produced_kg"].fillna(0).astype(float)) + list(filtered["Quantity_Sold_kg"].fillna(0).astype(float))

    fig = go.Figure(data=[go.Sankey(
        arrangement="snap",
        node=dict(
            pad=20,
            thickness=20,
            label=labels,
            color="rgba(56, 128, 255, 0.8)",
        ),
        link=dict(
            source=all_source,
            target=all_target,
            value=all_value,
            color="rgba(79, 140, 255, 0.35)",
        ),
    )])
    fig.update_layout(title="Farmer to distributor flow", template="plotly_white")
    return fig
