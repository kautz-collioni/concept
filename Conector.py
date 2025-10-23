import warnings
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pygam import *
import statsmodels.formula.api as smf
from statsmodels.tsa.seasonal import STL
from plotly.subplots import make_subplots
import nbformat

warnings.simplefilter(action = "ignore")

database_vendas = pd.read_csv("data/Cafeteria Fictícia Receitas.csv")

column_map = {
	"date": "sale_date",
    "money": "price",
    "coffee_name": "item"
#   "column_name": "quantity_venda"
}

valid_columns = []
for column_name in database_vendas.columns:
    if column_name in column_map.keys():
        valid_columns.append(column_name)

database_vendas = database_vendas[valid_columns]
database_vendas.rename(columns = column_map, inplace = True)

database_vendas.head(10)

database_compras = pd.read_csv("data/Cafeteria Fictícia Custos.csv") # database_estoques

column_map = {
   "insumo": "insumo",
   "quantity_received": "quantity_received",
   "unit_cost": "unit_cost",
   "date_received": "date_received",
}

valid_columns = []
for column_name in database_compras.columns:
    if column_name in column_map.keys():
        valid_columns.append(column_name)

database_compras = database_compras[valid_columns]
database_compras.rename(columns = column_map, inplace = True)

database_compras.head(10)

database_balanco = pd.read_csv("data/Cafeteria Fictícia Balanço.csv", sep=';', decimal=',', thousands='.')

column_map = {
   "Item": "Item",
   "1T 2024": "1T 2024", # As colunas são os anos
   "2T 2024": "2T 2024",
   "3T 2024": "3T 2024",
   "4T 2024": "4T 2024",
   "1T 2025": "1T 2025",
   "2T 2025": "2T 2025",
   "3T 2025": "3T 2025",
   "4T 2025": "4T 2025",
}

valid_columns = []
for column_name in database_balanco.columns:
    if column_name in column_map.keys():
        valid_columns.append(column_name)

database_balanco = database_balanco[valid_columns]
database_balanco.rename(columns = column_map, inplace = True)

database_balanco.head(10)

sales_summary = database_vendas.groupby(["item", "price"]).size().reset_index(name = "quantity")

figure1 = px.scatter(
    sales_summary, x = "quantity", y = "price", color = "item", trendline = "ols",
    labels = {"price": "Preço (R$)", "quantity": "Quantidade", "item": "Item"},
    title = "Análise Exploratória — Demandas Inversas", width = 1000, height = 500
)

figure1.update_layout(
    title_font_size = 18, font = dict(size = 14, family = "Arial", color = "black"),
    plot_bgcolor = "white", paper_bgcolor = "white",
    legend = dict(title = "", borderwidth = 0, font_size = 12, bgcolor = "rgba(0,0,0,0)"),
    xaxis = dict(showgrid = True, gridcolor = "lightgrey", zeroline = False, title_font_size = 14),
    yaxis = dict(showgrid = True, gridcolor = "lightgrey", zeroline = False, title_font_size = 14)
)

# figure1.show()

figure2 = px.violin(
    database_vendas, x = "item",  y = "price", color = "item", box = False, points = "all",
    labels = {"price": "Preço (R$)", "item": "Item"},
    title = "Análise Exploratória — Distribuições de Preços", width = 1000, height = 500
)

figure2.update_layout(
    title_font_size = 18, font = dict(size = 14, family = "Arial", color = "black"),
    plot_bgcolor = "white", paper_bgcolor = "white",
    showlegend = False,
    xaxis = dict(showgrid = True, gridcolor = "lightgrey", zeroline = False, title_font_size = 14),
    yaxis = dict(showgrid = True, gridcolor = "lightgrey", zeroline = False, title_font_size = 14)
)

# figure2.show()

elasticities = []

latest_prices = database_vendas.sort_values("sale_date").groupby("item").tail(1)
latest_prices = latest_prices.set_index("item")["price"]

for item in sales_summary["item"].unique():
    item_data = sales_summary[sales_summary["item"] == item]

    item_data["quantity"] = np.log(item_data["quantity"])
    item_data["price"] = np.log(item_data["price"])

    log_log = smf.ols("quantity ~ price", data = item_data).fit()
    beta_0, beta_1 = log_log.params

    P0 = latest_prices[item]
    Q0 = beta_0 + beta_1 * P0

    current_elasticity = beta_1 * (P0 / Q0)

    elasticities.append({
        "item": item,
        "current_price": P0,
        "predicted_quantity": Q0,
        "current_elasticity": np.abs(current_elasticity)
    })

elasticities = pd.DataFrame(elasticities)

figure3 = px.bar(
    elasticities,
    x = "item", y = "current_elasticity", color = "item",
    labels = {"item": "Item", "current_elasticity": "Nível"},
    title = "Análise Exploratória — Elasticidades-preço da Demanda Atuais", width = 1000, height = 500
)

for index, row in elasticities.iterrows():
    figure3.add_annotation(
        x = row["item"], y = row["current_elasticity"],
        text = f"<b>{row["current_elasticity"]:.2f}</b>",
        showarrow = False, font = dict(color = "white", size = 12),
        align = "center", bordercolor = "black",
        borderwidth = 1, bgcolor = "black", opacity = 0.8
    )

figure3.update_layout(
    title_font_size = 18,
    font = dict(size = 14, family = "Arial", color = "black"),
    plot_bgcolor = "white",
    paper_bgcolor = "white",
    legend = dict(title = "", borderwidth = 0, font_size = 12, bgcolor = "rgba(0,0,0,0)"),
    xaxis = dict(showgrid = True, gridcolor = "lightgrey", zeroline = False, title_font_size = 14),
    yaxis = dict(showgrid = True, gridcolor = "lightgrey", zeroline = False, title_font_size = 14)
)

# figure3.show()

# Tratamento de dados

accumulated_revenue = (database_vendas.groupby(["sale_date", "item"])["price"]
                 .sum().groupby(level = 1 ).cumsum().reset_index(name = "accumulated_revenue"))

accumulated_revenue["accumulated_revenue"] /= 1000

##################################################################################################################

figure4 = px.line(accumulated_revenue, x = "sale_date", y = "accumulated_revenue", color = "item",
               labels = {"sale_date": "Data", "accumulated_revenue": "Receita acumulada (mil R$)", "item": "Item"},
               title = "Análise Exploratória — Receitas Acumuladas", width = 1000, height = 500)

figure4.update_layout(
    title_font_size = 18, font = dict(size = 14, family = "Arial", color = "black"),
    plot_bgcolor = "white", paper_bgcolor = "white",
    legend = dict(title = "", font_size = 12, bgcolor = "rgba(0,0,0,0)"),
    xaxis = dict(showgrid = True, gridcolor = "lightgrey", zeroline = False, title_font_size = 14, tickformat = "%d/%m/%Y"),
    yaxis = dict(showgrid = True, gridcolor = "lightgrey", zeroline = False, title_font_size = 14)
)

# figure4.show()

daily_revenue = (database_vendas.groupby(["sale_date", "item"])["price"]
                 .sum().reset_index(name = "daily_revenue"))

figure5 = px.line(
    daily_revenue, x = "sale_date", y = "daily_revenue", color = "item",
    labels = {"sale_date": "Data", "daily_revenue": "Receita diária (R$)", "item": "Item"},
    title = "Análise Exploratória — Receitas Diárias", width = 1000, height = 500
)

figure5.update_layout(
    title_font_size = 18, font = dict(size = 14, family = "Arial", color = "black"),
    plot_bgcolor = "white", paper_bgcolor = "white",
    legend = dict(title = "", font_size = 12, bgcolor = "rgba(0,0,0,0)"),
    xaxis = dict(showgrid = True, gridcolor = "lightgrey", zeroline = False, title_font_size = 14, tickformat = "%d/%m/%Y"),
    yaxis = dict(showgrid = True, gridcolor = "lightgrey", zeroline = False, title_font_size = 14)
)

# figure5.show()

database_vendas["sale_date"] = pd.to_datetime(database_vendas["sale_date"])

translated_weekdays = {0: "Segunda-feira", 1: "Terça-feira", 2: "Quarta-feira", 3: "Quinta-feira", 4: "Sexta-feira", 5: "Sábado", 6: "Domingo"}
database_vendas["weekday"] = database_vendas["sale_date"].dt.dayofweek.map(translated_weekdays)

weekdays_revenue = (database_vendas.groupby(["sale_date", "weekday"])["price"]
                   .mean().reset_index(name = "weekdays_revenue"))

weekdays_revenue["weekday"] = pd.Categorical(weekdays_revenue["weekday"], ordered = True)

figure6 = px.line(
    weekdays_revenue, x = "sale_date", y = "weekdays_revenue", color = "weekday",
    labels = {"sale_date": "Data", "weekdays_revenue": "Receita média (R$)", "weekday": "Dia da semana"},
    title = "Análise Exploratória — Receitas Médias por Dia da Semana", width = 1000, height = 500
)

figure6.update_layout(
    title_font_size = 18,
    font = dict(size = 14, family = "Arial", color = "black"),
    plot_bgcolor = "white",
    paper_bgcolor = "white",
    legend = dict(title = "", font_size = 12, bgcolor = "rgba(0,0,0,0)"),
    xaxis = dict(showgrid = True, gridcolor = "lightgrey", zeroline = False, title_font_size = 14, tickformat = "%d/%m/%Y"),
    yaxis = dict(showgrid = True, gridcolor = "lightgrey", zeroline = False, title_font_size = 14)
)

# figure6.show()

daily_revenue = (database_vendas.groupby(["sale_date", "item"])["price"]
                 .sum().reset_index(name="daily_revenue"))

daily_revenue["sale_date"] = pd.to_datetime(daily_revenue["sale_date"])
daily_revenue = daily_revenue.set_index("sale_date")

weekly_revenue = (daily_revenue.groupby("item")
                  .resample("W")["daily_revenue"]
                  .mean()
                  .reset_index())

weekly_revenue["total_week"] = weekly_revenue.groupby("sale_date")["daily_revenue"].transform("sum")
weekly_revenue["percentage_revenue"] = weekly_revenue["daily_revenue"] / weekly_revenue["total_week"] * 100

figure7 = px.area(
    weekly_revenue, 
    x = "sale_date", y = "percentage_revenue", color = "item",
    labels = {"sale_date": "Data", "percentage_revenue": "Participação", "item": "Item"},
    title = "Análise Exploratória — Composição Dinâmica da Receita", width = 1000, height = 500
)

figure7.update_layout(
    title_font_size = 18,
    font = dict(size = 14, family = "Arial", color = "black"),
    plot_bgcolor = "white",
    paper_bgcolor = "white",
    legend = dict(title = "", font_size = 12, bgcolor = "rgba(0,0,0,0)"),
    xaxis = dict(showgrid = True, gridcolor = "lightgrey", zeroline = False, title_font_size = 14, tickformat = "%d/%m/%Y"),
    yaxis = dict(showgrid = True, gridcolor = "lightgrey", zeroline = False, title_font_size = 14, ticksuffix = "%")
)

# figure7.show()

optimal_prices = []
gam_results = {}

for item in sales_summary["item"].unique():
    item_data = sales_summary[sales_summary["item"] == item]

    price_values = item_data[["price"]].values
    quantity_values = item_data["quantity"].values

    gam = PoissonGAM(s(0, n_splines = 5, spline_order = 3, constraints = "monotonic_dec")).gridsearch(price_values, quantity_values)
    price_range = np.linspace(price_values.min(), price_values.max(), 100)

    demand_estimated = gam.predict(price_range)
    revenue_estimated = price_range * demand_estimated / 1000

    optimal_index = np.argmax(revenue_estimated)
    optimal_price = price_range[optimal_index]
    optimal_quantity = demand_estimated[optimal_index]

    optimal_prices.append({
        "item": item,
        "optimal_price": round(optimal_price, 2),
        "expected_quantity": round(optimal_quantity, 2),
        "expected_revenue": round(revenue_estimated[optimal_index], 2)
    })

    gam_results[item] = {
        "price_range": price_range,
        "demand_estimated": demand_estimated,
        "revenue_estimated": revenue_estimated,
        "optimal_price": optimal_price,
        "optimal_quantity": optimal_quantity
    }

figure8 = go.Figure()

colors = ["#1F77B4", "#FF7F0E", "#2CA02C", "#D62728", "#9467BD", 
          "#8C564B", "#E377C2", "#7F7F7F", "#BCBD22", "#17BECF"]

for index, item in enumerate(sales_summary["item"].unique()):
    item_data = sales_summary[sales_summary["item"] == item]
    result = gam_results[item]
    color = colors[index % len(colors)]
    visible = (item == sales_summary["item"].unique()[0])

    figure8.add_trace(go.Scatter(
        x = item_data["price"], y = item_data["quantity"], 
        mode = "markers", name = "Observado",
        marker = dict(size = 8, color = color, opacity = 0.6),
        visible = visible, legendgroup = "observed", showlegend = True
    ))

    figure8.add_trace(go.Scatter(
        x = result["price_range"], y = result["demand_estimated"],
        mode = "lines", name = "Demanda estimada",
        line = dict(color = color, width = 2),
        visible = visible, legendgroup = "demand", showlegend = True
    ))

    figure8.add_trace(go.Scatter(
        x = result["price_range"], y = result["revenue_estimated"],
        mode = "lines", name = "Receita",
        line = dict(color = color, dash = "dot", width = 2),
        yaxis = "y2", visible = visible, 
        legendgroup = "revenue", showlegend = True
    ))

    figure8.add_trace(go.Scatter(
        x = [result["optimal_price"]], y = [result["optimal_quantity"]],
        mode = "markers+text", text = [f"Ótimo: R$ {result["optimal_price"]:.2f}"],
        textposition = "top center", marker = dict(color = color, size = 10),
        name = "Ótimo", visible = visible, 
        legendgroup = "optimal", showlegend = True
    ))

buttons = []

for item in sales_summary["item"].unique():
    buttons.append({
        "label": item, "method": "update",
        "args": [{"visible": [item == coffee for coffee in sales_summary["item"].unique() for _ in range(4)],
                  "title": f"Generalized Additive Model (GAM)"}]
    })

figure8.update_layout(
    title = f"Generalized Additive Model (GAM)",
    title_font_size = 18, font = dict(size = 14, family = "Arial", color = "black"),
    width = 1000, height = 500, plot_bgcolor = "white", paper_bgcolor = "white",
    xaxis = dict(title = "Preço (R$)", showgrid = True, gridcolor = "lightgrey", 
                 zeroline = False, title_font_size = 14),
    yaxis = dict(title = "Quantidade", showgrid = True, gridcolor = "lightgrey", 
                 zeroline = False, title_font_size = 14),
    yaxis2 = dict(title = "Receita (mil R$)", overlaying = "y", side = "right",
                  showgrid = False, zeroline = False, title_font_size = 14),
    legend = dict(title = "", borderwidth = 0, font_size = 12, 
                  bgcolor = "rgba(0,0,0,0)", orientation = "v", x = 1.08, y = 1),
    updatemenus = [dict(
        buttons = buttons, direction = "down", showactive = True,
        x = 1.0, xanchor = "right", y = 1.15, yanchor = "top"
    )]
)

# figure8.show()

optimal_elasticities = []

for item in sales_summary["item"].unique():
    result = gam_results[item]
    price_range = result["price_range"]
    demand_estimated = result["demand_estimated"]
    optimal_index = np.argmax(result["revenue_estimated"])

    optimal_P = price_range[optimal_index]
    optimal_Q = demand_estimated[optimal_index]

    if optimal_index > 0 and optimal_index < len(price_range) - 1:
        dP = price_range[optimal_index + 1] - price_range[optimal_index - 1]
        dQ = demand_estimated[optimal_index + 1] - demand_estimated[optimal_index - 1]
        dQ_dP = dQ / dP
    elif optimal_index == 0:
        dP = price_range[1] - price_range[0]
        dQ = demand_estimated[1] - demand_estimated[0]
        dQ_dP = dQ / dP
    else:
        dP = price_range[-1] - price_range[-2]
        dQ = demand_estimated[-1] - demand_estimated[-2]
        dQ_dP = dQ / dP

    optimal_elasticity = dQ_dP * (optimal_P / optimal_Q)

    optimal_elasticities.append({
        "item": item,
        "optimal_price": optimal_P,
        "predicted_quantity": optimal_Q,
        "optimal_elasticity": np.abs(optimal_elasticity)
    })

optimal_elasticities = pd.DataFrame(optimal_elasticities)

figure9 = px.bar(
    optimal_elasticities,
    x = "item", y = "optimal_elasticity", color = "item",
    labels = {"item": "Item", "optimal_elasticity": "Nível"},
    title = "Elasticidades-preço da Demanda Ótimas", width = 1000, height = 500
)

for index, row in optimal_elasticities.iterrows():
    figure9.add_annotation(
        x = row["item"], y = row["optimal_elasticity"],
        text = f"<b>{row["optimal_elasticity"]:.2f}</b>",
        showarrow = False, font = dict(color = "white", size = 12),
        align = "center", bordercolor = "black",
        borderwidth = 1, bgcolor = "black", opacity = 0.8
    )

figure9.update_layout(
    title_font_size = 18,
    font = dict(size = 14, family = "Arial", color = "black"),
    plot_bgcolor = "white",
    paper_bgcolor = "white",
    legend = dict(title = "", borderwidth = 0, font_size = 12, bgcolor = "rgba(0,0,0,0)"),
    xaxis = dict(showgrid = True, gridcolor = "lightgrey", zeroline = False, title_font_size = 14),
    yaxis = dict(showgrid = True, gridcolor = "lightgrey", zeroline = False, title_font_size = 14)
)

# figure9.show()

daily_revenue = (database_vendas.groupby(["sale_date", "item"])["price"]
                 .sum().reset_index(name = "daily_revenue"))

daily_revenue["sale_date"] = pd.to_datetime(daily_revenue["sale_date"])

items_list = list(sales_summary["item"].unique())

decomposition_frames = []

for index, item in enumerate(items_list):
    series = (daily_revenue.loc[daily_revenue["item"] == item, ["sale_date", "daily_revenue"]]
                                  .set_index("sale_date")
                                  .sort_index()
                                  .asfreq("D"))

    series["daily_revenue"] = series["daily_revenue"].fillna(0.0)

    stl = STL(series["daily_revenue"], period = 7, robust = True)
    stl_result = stl.fit()

    decomposition_frame = pd.DataFrame({
        "sale_date": series.index,
        "item": item,
        "trend": stl_result.trend,
        "seasonal": stl_result.seasonal,
        "residual": stl_result.resid
    }).reset_index(drop = True)

    decomposition_frames.append(decomposition_frame)

decomposition_data = pd.concat(decomposition_frames, ignore_index = True)

figure10 = make_subplots(
    rows = 3, cols = 1, shared_xaxes = True, vertical_spacing = 0.08,
    subplot_titles = ("Tendência", "Sazonalidade", "Resíduo")
)

trace_visibility = []

for index, item in enumerate(items_list):
    color = colors[index % len(colors)]
    slice = decomposition_data[decomposition_data["item"] == item]

    is_visible = (index == 0)

    figure10.add_trace(
        go.Scatter(
            x = slice["sale_date"], y = slice["trend"],
            mode = "lines", name = "Tendência",
            line = dict(width = 2, color = color),
            visible = is_visible,
            showlegend = True
        ),
        row = 1, col = 1
    )
    trace_visibility.append(is_visible)

    figure10.add_trace(
        go.Scatter(
            x = slice["sale_date"], y = slice["seasonal"],
            mode = "lines", name = "Sazonalidade",
            line = dict(width = 2, color = color),
            visible = is_visible,
            showlegend = True
        ),
        row = 2, col = 1
    )
    trace_visibility.append(is_visible)

    figure10.add_trace(
        go.Scatter(
            x = slice["sale_date"], y = slice["residual"],
            mode = "lines", name = "Resíduo",
            line = dict(width = 2, color = color, dash = "dot"),
            visible = is_visible,
            showlegend = True
        ),
        row = 3, col = 1
    )
    trace_visibility.append(is_visible)

buttons = []
traces_per_item = 3
total_traces = traces_per_item * len(items_list)

for index, item in enumerate(items_list):
    visibility_mask = [False] * total_traces
    start = index * traces_per_item
    for k in range(traces_per_item):
        visibility_mask[start + k] = True

    buttons.append(dict(
        label = item,
        method = "update",
        args = [
            {"visible": visibility_mask},
            {"title": f"Decomposição de Receita — {item}"}
        ]
    ))

figure10.update_layout(
    title = f"Tendência, Sazonalidade e Resíduo",
    title_font_size = 18,
    font = dict(size = 14, family = "Arial", color = "black"),
    width = 1000, height = 700,
    plot_bgcolor = "white", paper_bgcolor = "white",
    legend = dict(title = "", borderwidth = 0, font_size = 12, bgcolor = "rgba(0,0,0,0)"),
    updatemenus = [dict(
        buttons = buttons, direction = "down", showactive = True,
        x = 1.0, xanchor = "right", y = 1.15, yanchor = "top"
    )]
)

figure10.update_xaxes(
    showgrid = True, gridcolor = "lightgrey", zeroline = False, title_font_size = 14,
    tickformat = "%d/%m/%Y", row = 3, col = 1, title_text = "Data"
)
figure10.update_xaxes(
    showgrid = True, gridcolor = "lightgrey", zeroline = False, tickformat = "%d/%m/%Y", row = 1, col = 1
)
figure10.update_xaxes(
    showgrid = True, gridcolor = "lightgrey", zeroline = False, tickformat = "%d/%m/%Y", row = 2, col = 1
)

figure10.update_yaxes(title_text = "Nível", showgrid = True, gridcolor = "lightgrey",
                     zeroline = False, title_font_size = 14, row = 1, col = 1)
figure10.update_yaxes(title_text = "Nível", showgrid = True, gridcolor = "lightgrey",
                     zeroline = False, title_font_size = 14, row = 2, col = 1)
figure10.update_yaxes(title_text = "Nível", showgrid = True, gridcolor = "lightgrey",
                     zeroline = False, title_font_size = 14, row = 3, col = 1)

# figure10.show()

# TRATAMENTO DOS DADOS
# Duplicar as bases para não alterar na origem dos dados
df_custos = database_compras
df_receitas = database_vendas

df_custos['date_received'] = pd.to_datetime(df_custos['date_received'])
df_receitas['sale_date'] = pd.to_datetime(df_receitas['sale_date'])

# Calcular saídas (custos)
df_custos['saidas'] = df_custos['quantity_received'] * df_custos['unit_cost']
df_custos_mensal = df_custos.groupby(pd.Grouper(key='date_received', freq='M'))['saidas'].sum().reset_index()
df_custos_mensal.rename(columns={'date_received': 'data'}, inplace=True)

# Calcular entradas (receitas)
df_receitas_mensal = df_receitas.groupby(pd.Grouper(key='sale_date', freq='M'))['price'].sum().reset_index()
df_receitas_mensal.rename(columns={'sale_date': 'data', 'price': 'entradas'}, inplace=True)

# Criar range completo de datas
data_inicio = df_custos['date_received'].min().replace(day=1)
data_fim = df_receitas['sale_date'].max().replace(day=1) + pd.offsets.MonthEnd(1)

# Criar DataFrame com todas as datas mensais
all_dates = pd.date_range(start=data_inicio, end=data_fim, freq='M', name='data')
df_completo = pd.DataFrame({'data': all_dates})

# Juntar todos os dados
df_fc = df_completo.merge(df_custos_mensal, on='data', how='left')
df_fc = df_fc.merge(df_receitas_mensal, on='data', how='left')

# Preencher valores NaN com 0
df_fc['saidas'] = df_fc['saidas'].fillna(0)
df_fc['entradas'] = df_fc['entradas'].fillna(0)

# Muda o sinal das saídas *Avaliar necessidade dependendo da estrutura da base de dados
df_fc['saidas'] = df_fc['saidas'] * -1

# Formatar data como string (opcional)
df_fc['data'] = df_fc['data'].dt.strftime('%Y-%m')

# Definir data como índice
#df_fc.set_index('data', inplace=True)

# Margem = (Receita - Custo) / Receita
df_fc['margem_percentual'] = (df_fc['entradas'] - df_fc['saidas'].abs()) / df_fc['entradas']
# Tratar casos onde 'entradas' é 0 (para evitar NaN/Inf, definimos a margem como 0)
df_fc['margem_percentual'].fillna(0, inplace=True) 
df_fc.loc[df_fc['entradas'] == 0, 'margem_percentual'] = 0 



df_fc_long = df_fc.melt(
    id_vars=["data"], 
    value_vars=["entradas", "saidas"], 
    var_name="type", 
    value_name="valor"
)

figure11 = go.Figure()

# 1. Adiciona as barras para cada tipo
for type_value in df_fc_long['type'].unique():
    df_filtered = df_fc_long[df_fc_long['type'] == type_value]
    figure11.add_trace(
        go.Bar(
            x=df_filtered["data"],
            y=df_filtered["valor"],
            name=type_value,
        )
    )

# 2. Adiciona a linha da Margem Percentual
figure11.add_trace(
    go.Scatter(
        x=df_fc["data"],
        y=df_fc["margem_percentual"],
        name="Margem (%)",
        mode='lines+markers+text',
        yaxis='y2',
        line=dict(color='darkgrey', width=3),
        marker=dict(symbol='circle', size=8, color='darkgrey'),
        text=[f'{p*100:.1f}%' for p in df_fc["margem_percentual"]],
        textposition="top center",
        textfont=dict(color='black', size=11, weight='bold')
    )
)

# 3. Cria as anotações
annotations = []
# Anotações para as barras
for index, row in df_fc_long.iterrows():
    # As anotações são aplicadas em 'entradas' e 'saidas'
    annotations.append(
        dict(
            x=row["data"],
            y=row["valor"],
            text=f"<b>{row['valor']:.2f}</b>",
            showarrow=False,
            font=dict(color="white", size=12),
            align="center",
            bordercolor="black",
            borderwidth=1,
            bgcolor="black",
            opacity=0.8,
            xref="x",
            yref="y",
        )
    )
        
# 6. Atualiza o layout
figure11.update_layout(
    annotations=annotations,
    barmode="relative",
    title_font_size=18,
    font=dict(size=14, family="Arial", color="black"),
    plot_bgcolor="white",
    paper_bgcolor="white",
    xaxis=dict(
        showgrid=True,
        gridcolor="lightgrey",
        zeroline=False,
        title_font_size=14
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor="lightgrey",
        title_font_size=14,
    ),
    yaxis2=dict(
        title='Margem (%)',
        overlaying='y',
        side='right',
        showgrid=False,
        tickformat=".1%",
    ),
    legend=dict(
        title="",
        borderwidth=0,
        font_size=12,
        bgcolor="rgba(0,0,0,0)",
        orientation="v",
        yanchor="top",
        y=0.95,
        xanchor="left",
        x=1.05
    ),
    title="Fluxo de Caixa - Mensal",
    width=900,
    height=500,
)

#figure11.show()

# Anualizar os dados históricos

# Extrair ano diretamente do índice (que está no formato 'YYYY-MM')
df_anual = df_fc.copy()
df_anual.set_index('data', inplace=True)
df_anual['ano'] = df_anual.index.str[:4].astype(int)
df_anual = df_anual.groupby('ano').agg({
    'saidas': 'sum',
    'entradas': 'sum'
}).reset_index()

# Projeção para 5 anos com crescimento de 10% (Receitas)
ultimo_ano_historico = df_anual['ano'].max()
ultima_receita = df_anual[df_anual['ano'] == ultimo_ano_historico]['entradas'].values[0]

anos_projecao = range(ultimo_ano_historico + 1, ultimo_ano_historico + 6)
projecao_receitas = []

receita_atual = ultima_receita
for ano in anos_projecao:
    receita_atual *= 1.10 # Crescimento de 10%
    projecao_receitas.append({
        'ano': ano,
        'Receitas': receita_atual
})

df_projecao_receita = pd.DataFrame(projecao_receitas)


# Criar DataFrame completo de Receitas com histórico + projeção
df_completo_receita = df_anual[['ano', 'entradas']].copy()
df_completo_receita.rename(columns={'entradas': 'Receitas'}, inplace=True)

df_completo_receita = pd.concat([
    df_completo_receita,
    df_projecao_receita
], ignore_index=True)


# PROJEÇÃO DE DESPESAS E CÁLCULO DA MARGEM

# Projeção para 5 anos com crescimento de 10% (Despesas)
# Pega a última despesa histórica
ultima_despesa = df_anual[df_anual['ano'] == ultimo_ano_historico]['saidas'].values[0]

projecao_despesas = []
despesa_atual = ultima_despesa

for ano in anos_projecao:
    despesa_atual *= 1.10 # Crescimento de 10%
    projecao_despesas.append({
        'ano': ano,
        'Despesas': despesa_atual
    })

df_projecao_despesa = pd.DataFrame(projecao_despesas)


# DataFrame completo de Despesas com histórico + projeção
df_completo_despesa = df_anual[['ano', 'saidas']].copy()
df_completo_despesa.rename(columns={'saidas': 'Despesas'}, inplace=True)

df_completo_despesa = pd.concat([
    df_completo_despesa,
    df_projecao_despesa
], ignore_index=True)


# DataFrame Mestre e Calcular a Margem
# Combina Receitas e Despesas
df_mestre = pd.merge(df_completo_receita, df_completo_despesa, on='ano', how='inner')

# Calcula a Margem (Receitas - Despesas)
df_mestre['Margem'] = df_mestre['Receitas'] - df_mestre['Despesas']

# Define o ano como índice
df_pivot = df_mestre.set_index('ano')

# Transpõe (inverte) o DataFrame para ter Anos nas Colunas e Variáveis nas Linhas
df_tabela_final = df_pivot.T

# Limpar o nome do índice
df_tabela_final.index.name = None

print(df_tabela_final)

df_liquidez = database_balanco.copy()

quarter_cols = df_liquidez.columns[1:].tolist()

# Isola Ativo Circulante (AC) e Passivo Circulante (PC)
ac_values = df_liquidez[df_liquidez['Item'] == 'Ativo Circulante'].iloc[0][quarter_cols]
pc_values = df_liquidez[df_liquidez['Item'] == 'Passivo Circulante'].iloc[0][quarter_cols]

# Calcula a Liquidez Corrente: LC = Ativo Circulante / Passivo Circulante
liquidez_corrente = ac_values / pc_values

# Cria o DataFrame no formato "long" (df_fc_long equivalente) para Plotly
df_liquidez_ratio = pd.DataFrame({
    'data': quarter_cols,
    'valor': liquidez_corrente.values
})


# 3. Configuração do Gráfico de Linhas com go.Figure()
figure12 = go.Figure()

# Adiciona o Trace de Linhas para a Liquidez Corrente
figure12.add_trace(go.Scatter(
    x=df_liquidez_ratio["data"],
    y=df_liquidez_ratio["valor"],
    mode='lines+markers', # Linha e marcadores para cada ponto
    name='Liquidez Corrente',
    #line=dict(color='#006400', width=4), # Linha verde escura
    marker=dict(size=10),#, color='#3CB371', line=dict(width=2, color='#006400')),
    hovertemplate="<b>%{x}</b><br>Liquidez Corente: %{y:.2f}<extra></extra>"
))


# 4. Cria a lista de anotações (adaptada para o novo DataFrame e estilo)
annotations = []
for index, row in df_liquidez_ratio.iterrows():
    if pd.notna(row['valor']):
        annotations.append(
            dict(
                x=row["data"],
                y=row["valor"],
                text=f"<b>{row['valor']:.2f}</b>", # Formato com 2 casas decimais
                showarrow=False,
                font=dict(color="white", size=12),
                align="center",
                bordercolor="black",
                borderwidth=1,
                bgcolor="black", # Cor de fundo da anotação (verde escuro)
                opacity=0.8,
                xanchor="center",
                yanchor="bottom",
                yshift=10, # Desloca o texto um pouco acima do marcador
                xref="x", 
                yref="y", 
            )
        )

# 5. Aplica os ajustes finais de layout (incluindo as anotações)
figure12.update_layout(
    annotations=annotations, # Adiciona as anotações

    # 'barmode' é ignorado para gráfico de linha/scatter, mas mantido da sua template
    # barmode="relative", 

    # Configurações de Título e Fonte Geral
    title= "Liquidez Corrente",
    title_font_size = 18,
    font = dict(size = 14, family = "Arial", color = "black"),
    
    # Cores de Fundo (Ajustado para branco, seguindo o estilo de figure10)
    plot_bgcolor = "white",
    paper_bgcolor = "white",
    
    # Configurações do Eixo X
    xaxis = dict(
        title = "Trimestre", # Título para o Eixo X
        showgrid = True, 
        gridcolor = "lightgrey", 
        zeroline = False, 
        title_font_size = 14
    ),
    
    # Configurações do Eixo Y
    yaxis = dict(
        title = "Liquidez Corrente", # Título para o Eixo Y
        showgrid = True, 
        gridcolor = "lightgrey", 
        zeroline = False, 
        title_font_size = 14,
        tickformat=".2f" # Força 2 casas decimais nos ticks
    ),

    # Configurações da Legenda
    legend = dict(
        title = "", 
        borderwidth = 0, 
        font_size = 12, 
        bgcolor = "rgba(0,0,0,0)",
        orientation="v", 
        yanchor="top", 
        y=0.95, 
        xanchor="left", 
        x=1.05 
    ),
    
    width=900,
    height=500,
)

#figure12.show()


# Entradas de estoque
entradas = (
    database_compras
    .rename(columns={'insumo': 'item', 'date_received': 'data'})
    .assign(qtd=lambda x: x['quantity_received'])
    [['data', 'item', 'qtd']]
)

# Saídas de estoque (cada venda = -1 unidade)
saidas = (
    database_vendas
    .rename(columns={'sale_date': 'data'})
    .assign(qtd=-1)
    [['data', 'item', 'qtd']]
)

# Combina entradas e saídas
estoque = pd.concat([entradas, saidas], ignore_index=True)
estoque['data'] = pd.to_datetime(estoque['data'])

# Ordena por data
estoque = estoque.sort_values(by=['item', 'data'])

# Calcula o estoque acumulado
estoque['estoque'] = estoque.groupby('item')['qtd'].cumsum()

# Cria uma grade de datas para preencher eventuais dias sem movimento
estoque_completo = (
    estoque.groupby('item', group_keys=False)
    .apply(lambda g: (
        g.set_index('data')
         .resample('D')
         .sum()
         .assign(item=g.name)
         .reset_index()
    ))
)

# Calcula o estoque acumulado e preenche valores ausentes
estoque_completo['estoque'] = (
    estoque_completo.groupby('item')['qtd']
    .cumsum()
)

# Preenche valores ausentes propagando o último estoque conhecido
estoque_completo['estoque'] = (
    estoque_completo.groupby('item')['estoque']
    .fillna(method='ffill')
    .fillna(0)
)

# --- Gráfico interativo estilizado ---
figure13 = px.line(
    estoque_completo,
    x='data',
    y='estoque',
    color='item',
    title='Evolução do Estoque por Produto',
    labels={'data': 'Data', 'estoque': 'Quantidade em Estoque', 'item': 'Produto'}
)

# Remove os markers (deixa apenas a linha)
figure13.update_traces(mode='lines')

# Ajusta o layout visual
figure13.update_layout(
    title_font_size=18,
    font=dict(size=14, family="Arial", color="black"),
    plot_bgcolor="white",
    paper_bgcolor="white",
    legend=dict(title="", font_size=12, bgcolor="rgba(0,0,0,0)"),
    xaxis=dict(
        showgrid=True,
        gridcolor="lightgrey",
        zeroline=False,
        title_font_size=14,
        tickformat="%d/%m/%Y"
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor="lightgrey",
        zeroline=False,
        title_font_size=14
    ),
    hovermode='x unified',
    legend_title_text='Produto'
)

#figure13.show()

comparison_table = pd.DataFrame(optimal_prices)

comparison_table["current_price"] = comparison_table["item"].map(latest_prices)
comparison_table["percent_difference"] = (comparison_table["optimal_price"] - comparison_table["current_price"]) / comparison_table["current_price"] * 100
comparison_table["estimated_revenue"] = comparison_table["optimal_price"] * comparison_table["expected_quantity"]

comparison_table = comparison_table[[
    "item",
    "current_price",
    "optimal_price",
    "percent_difference",
    "expected_quantity",
    "estimated_revenue"
]]

comparison_table.columns = [
    "Item",
    "Preço atual (R$)",
    "Preço ótimo (R$)",
    "Diferença (%)",
    "Quantidade estimada",
    "Receita estimada (R$)"
]

# comparison_table.to_csv("Entregável - Tabela de Comparação.csv", sep = ";", decimal = ",", index = False, encoding = "utf-8-sig")

# revision = pd.read_csv("Entregável - Tabela de Comparação.csv", sep = ";", decimal = ",")
# revision.sample(5)

with open("Script Consolidado (12-10-2025 G).ipynb", "r", encoding = "utf-8") as f:
    nb = nbformat.read(f, as_version = 4)

code = ""
for cell in nb.cells:
    if cell.cell_type == "code":
        code += cell.source + "\n\n"

with open("Conector.py", "w", encoding="utf-8") as f:
    f.write(code)

