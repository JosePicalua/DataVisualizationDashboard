import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import plotly.express as px
from dash.dependencies import Input, Output, State, ALL
from dash import callback_context

# Cargar CSVs
df = pd.read_csv('dataset/part-data/annex1.csv')
df2 = pd.read_csv('dataset/part-data/datosLimpiosAnnexo2.csv')
df3 = pd.read_csv('dataset/part-data/annex3.csv')

# Crear columna de fecha completa
df2['FechaCompleta'] = pd.to_datetime(
    df2[['Year Sale', 'Month Sale', 'Day Sale']].rename(
        columns={'Year Sale': 'year', 'Month Sale': 'month', 'Day Sale': 'day'}
    )
)

df2['TotalVentas'] = df2['Quantity Sold (kilo)'] * df2['Unit Selling Price (RMB/kg)'] 

# Función para crear el histograma general
def graficar_histograma():
    df2['TotalVentasAgrupadas'] = df2['Quantity Sold (kilo)'] * df2['Unit Selling Price (RMB/kg)']
    ventas_agrupadas = df2.groupby('Item Code', as_index=False)['TotalVentasAgrupadas'].sum()
    df_join = pd.merge(df, ventas_agrupadas, on='Item Code', how='right')
    ventas_categoria = df_join.groupby(['Category Code', 'Category Name'], as_index=False)['TotalVentasAgrupadas'].sum()
    ventas_categoria = ventas_categoria.sort_values(by='TotalVentasAgrupadas', ascending=False)

    fig = px.bar(
        ventas_categoria,
        x='Category Name',
        y='TotalVentasAgrupadas',
        color='Category Name',
        title='Ventas por Categoría (Total)',
        text_auto='.2s'
    )
    fig.update_layout(
        plot_bgcolor='#000000',
        paper_bgcolor='#000000',
        font=dict(color='white'),
        xaxis=dict(color='white'),
        yaxis=dict(color='white'),
        title_font=dict(size=20),
        margin=dict(t=40, b=40, l=40, r=40)
    )
    return fig

# Nueva función para graficar ventas por año para un Item Code específico
def graficar_item_por_anio(item_code):
    # Calcular ventas por año para el Item Code específico
    df2['TotalVentasAgrupadas'] = df2['Quantity Sold (kilo)'] * df2['Unit Selling Price (RMB/kg)']
    item_ventas_por_anio = df2[df2['Item Code'] == item_code].groupby(['Year Sale'], as_index=False)['TotalVentasAgrupadas'].sum()
    
    # Obtener el nombre del item para mostrar en el título
    item_name = df[df['Item Code'] == item_code]['Item Name'].iloc[0] if not df[df['Item Code'] == item_code].empty else item_code
    
    fig = px.bar(
        item_ventas_por_anio,
        x='Year Sale',
        y='TotalVentasAgrupadas',
        title=f'Ventas por Año - {item_name} (Código: {item_code})',
        text_auto='.2s',
        color_discrete_sequence=['#00C49F']  # Color diferente para distinguir de otras gráficas
    )
    fig.update_layout(
        plot_bgcolor='#000000',
        paper_bgcolor='#000000',
        font=dict(color='white'),
        xaxis=dict(color='white', title='Año'),
        yaxis=dict(color='white', title='Total Ventas (RMB)'),
        title_font=dict(size=20),
        margin=dict(t=40, b=40, l=40, r=40)
    )
    return fig

def graficar_top_productos(category_code):
    df2['TotalVentasAgrupadas'] = df2['Quantity Sold (kilo)'] * df2['Unit Selling Price (RMB/kg)']
    ventas_agrupadas = df2.groupby('Item Code', as_index=False)['TotalVentasAgrupadas'].sum()
    df_join = pd.merge(df, ventas_agrupadas, on='Item Code', how='right')
    df_filtrado = df_join[df_join['Category Code'] == category_code]
    top_10_productos = df_filtrado.sort_values(by='TotalVentasAgrupadas', ascending=False).head(10)

    fig = px.bar(
        top_10_productos,
        x='Item Name',
        y='TotalVentasAgrupadas',
        color='Item Name',
        title=f'Top 10 Productos - Categoría {category_code}',
        text_auto='.2s'
    )
    fig.update_layout(
        plot_bgcolor='#000000',
        paper_bgcolor='#000000',
        font=dict(color='white'),
        xaxis=dict(color='white'),
        yaxis=dict(color='white'),
        title_font=dict(size=20),
        margin=dict(t=40, b=40, l=40, r=40)
    )
    return fig

# Inicializar app
app = dash.Dash(__name__)
server = app.server  # Esta línea es clave para Render

# Categorías únicas
categorias = df['Category Name'].unique()

# Layout - Incluye el histograma pre-renderizado
app.layout = html.Div([
    # Modal para explicación del proyecto
    html.Div([
        html.Div([
            html.H3("Dashboard de Análisis de Ventas", className="modal-title"),
            html.Hr(),
            html.P([
                "¡Bienvenido a tu ", 
                html.Strong("Panel de Control Inteligente de Ventas"), 
                "! Esta herramienta te permite visualizar y analizar datos de ventas de manera dinámica e interactiva."
            ], className="modal-intro"),
            html.P([
                "✨ ", 
                html.Strong("Explora tendencias por categorías"), 
                " y descubre qué productos generan más ingresos"
            ]),
            html.P([
                "📊 ", 
                html.Strong("Analiza el comportamiento anual"), 
                " de cualquier producto específico con solo un clic"
            ]),
            html.P([
                "💰 ", 
                html.Strong("Consulta métricas clave"), 
                ": ventas totales, devoluciones y porcentajes de rendimiento"
            ]),
            html.P([
                "📅 ", 
                html.Strong("Filtra por fechas"), 
                " para examinar períodos específicos y descubrir patrones estacionales"
            ]),
            html.P([
                "🔍 Para comenzar, selecciona una categoría en el menú desplegable superior o explora el histograma general de ventas por categoría."
            ], className="modal-instructions"),
            html.P("Haz clic en cualquier lugar fuera de este recuadro para comenzar.", className="modal-close-instruction"),
        ], className='modal-content')
    ], id='modal-explanation', className='modal', style={'display': 'block'}),

    # El resto de tu layout existente
    html.Div([
        html.Div([
            html.Label('Category Name', className='label'),
            dcc.Dropdown(
                id='dropdown-category',
                options=[{'label': cat, 'value': cat} for cat in categorias],
                placeholder='Select Category'
            )
        ], className='box'),

        html.Div([
            html.Label('Item Name', className='label'),
            dcc.Dropdown(id='dropdown-item', placeholder='Select Item')
        ], className='box'),

        html.Div([
            html.Label('Item Code', className='label'),
            html.Div(id='output-item-code', className='output')
        ], className='box'),

        html.Div([
            html.Label('Category Code', className='label'),
            html.Div(id='output-category-code', className='output')
        ], className='box'),
    ], className='container'),

    html.Div([
        html.Div([
            html.H4("Total Ventas"),
            html.Div(id='numero-ventas', className='numero')
        ], className='totalVenta'),

        html.Div([
            html.H4("Total Devoluciones"),
            html.Div(id='numero-devoluciones', className='numero')
        ], className='totalDevoluciones'),

        html.Div([
            html.H4("Porcentaje Ventas"),
            html.Div(id='numero-porcentaje', className='numero')
        ], className='porventajeVentas'),

        html.Div([
            html.H4("Registro de Ventas Unitarias"),
            html.Div(id='numero-total', className='numero')
        ], className='totalOperaciones'),

        html.Div([
            html.H4("Registros por Fecha"),
            dcc.DatePickerSingle(
                id='fecha-selector',
                placeholder='Selecciona una fecha',
                date=None,
                display_format='YYYY-MM-DD'
            )
        ], className='calendario'),

        html.Div([
            html.H4("Ventas"),
            # Inicializar con el gráfico directamente para que aparezca al cargar
            html.Div(id='histograma-ventas', children=[
                dcc.Graph(id='histograma-graph', figure=graficar_histograma())
            ])
        ], className='HistogramaVentas'),

        html.Div([
            html.H4("Productos"),
            html.Div(id='listado-productos'),
            dcc.Store(id='last-clicked-category', data=True),
            # Almacenar el último item code seleccionado
            dcc.Store(id='selected-item-code', data=None),
        ], className='listProductos'),
        
    ], className='parent'),

    html.Div([
    ], className='parentMetricas')
])

# Añade este callback para controlar el modal
# Versión mejorada del callback
@app.callback(
    Output('modal-explanation', 'style'),
    Input('modal-explanation', 'n_clicks'),
    State('modal-explanation', 'style'),
    prevent_initial_call=True
)
def toggle_modal(n_clicks, current_style):
    # Verificar si el clic fue en el modal o en su contenido
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'modal-explanation' and n_clicks:
        # Si ya estaba visible, lo ocultamos
        if current_style and current_style.get('display') == 'block':
            return {'display': 'none'}
    
    # Por defecto se mantiene como estaba
    return current_style

# Callback para actualizar ítems por categoría
@app.callback(
    Output('dropdown-item', 'options'),
    Input('dropdown-category', 'value')
)
def actualizar_items(categoria):
    if categoria is None:
        return []
    items_filtrados = df[df['Category Name'] == categoria]['Item Name'].unique()
    return [{'label': item, 'value': item} for item in items_filtrados]


# Callback para actualizar fechas disponibles por item
@app.callback(
    Output('fecha-selector', 'disabled'),
    Output('fecha-selector', 'min_date_allowed'),
    Output('fecha-selector', 'max_date_allowed'),
    Input('dropdown-item', 'value')
)
def actualizar_fechas(item_name):
    if item_name is None:
        return True, None, None

    fila = df[df['Item Name'] == item_name]
    if fila.empty:
        return True, None, None

    item_code = fila.iloc[0]['Item Code']
    fechas = df2[df2['Item Code'] == item_code]['FechaCompleta'].dropna()

    if fechas.empty:
        return True, None, None

    return False, fechas.min().date(), fechas.max().date()


# Callback para actualizar los números de ventas, devoluciones, porcentaje y total
@app.callback(
    Output('numero-ventas', 'children'),
    Output('numero-devoluciones', 'children'),
    Output('numero-porcentaje', 'children'),
    Output('numero-total', 'children'),
    Input('dropdown-item', 'value'),
    Input('fecha-selector', 'date')
)
def actualizar_por_item_y_fecha(item_name, fecha_seleccionada):
    if item_name is None:
        df_filtrado = df2.copy()
    else:
        fila = df[df['Item Name'] == item_name]
        if fila.empty:
            return '', '', '', ''
        item_code = fila.iloc[0]['Item Code']
        df_filtrado = df2[df2['Item Code'] == item_code]

    if fecha_seleccionada:
        fecha_dt = pd.to_datetime(fecha_seleccionada)
        df_filtrado = df_filtrado[df_filtrado['FechaCompleta'] == fecha_dt]

    df_filtrado['TotalVentas'] = df_filtrado['Quantity Sold (kilo)'] * df_filtrado['Unit Selling Price (RMB/kg)']
    total_ventas = df_filtrado[df_filtrado['Sale or Return'] == 1]['TotalVentas'].sum()
    total_ventas_str = f"{total_ventas:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")

    sale_return_counts = df_filtrado['Sale or Return'].value_counts()
    sale = int(sale_return_counts.get(1, 0))
    devolucion = int(sale_return_counts.get(0, 0))
    total = sale + devolucion

    porcentaje_ventas = f"{(sale / total * 100):.2f}%" if total > 0 else "0%"
    porcentaje_devolucion = f"{(devolucion / total * 100):.2f}%" if total > 0 else "0%"
    devolucion_str = f"{devolucion} ∼ {porcentaje_devolucion}"

    return total_ventas_str, devolucion_str, porcentaje_ventas, total


# Mostrar Item Code y Category Code, y almacenar el item code seleccionado
@app.callback(
    Output('output-item-code', 'children'),
    Output('output-category-code', 'children'),
    Output('selected-item-code', 'data'),
    Input('dropdown-item', 'value')
)
def mostrar_codigos(item_name):
    if item_name is None:
        return '', '', None
    
    fila = df[df['Item Name'] == item_name]
    if fila.empty:
        return '', '', None
    
    item_code = fila.iloc[0]['Item Code']
    category_code = fila.iloc[0]['Category Code']
    return item_code, category_code, item_code


@app.callback(
    Output('listado-productos', 'children'),
    Input('dropdown-item', 'value')
)
def generar_listado_productos(_):
    # 1. Total ventas por Item
    df2['TotalVentasAgrupadas'] = df2['Quantity Sold (kilo)'] * df2['Unit Selling Price (RMB/kg)']
    ventas_agrupadas = df2.groupby('Item Code', as_index=False)['TotalVentasAgrupadas'].sum()
    
    # 2. Unir con df para traer nombres y categorías
    df_join = pd.merge(df, ventas_agrupadas, on='Item Code', how='right')

    # 3. Agrupar jerárquicamente: Category Name > Category Code > Item Name
    categorias = []
    for (cat_name, cat_code), grupo_cat in df_join.groupby(['Category Name', 'Category Code']):
        items = []
        for _, fila in grupo_cat.iterrows():
            item_nombre = fila['Item Name']
            item_code = fila['Item Code']
            
        categoria_code_element = html.Details([
            html.Summary(cat_code, id={'type': 'category-code', 'index': int(cat_code)}, style={'cursor': 'pointer'}),
            html.Ul(items, style={'marginLeft': '20px'})
        ])

        categoria_name_element = html.Details([
            html.Summary(f"{cat_name}"),
            categoria_code_element
        ])

        categorias.append(categoria_name_element)

    return categorias


# Callback para actualizar el histograma
@app.callback(
    Output('histograma-ventas', 'children'),
    Output('last-clicked-category', 'data'),
    Input('dropdown-item', 'value'),
    Input('selected-item-code', 'data'),  # Agregar item_code como input
    Input({'type': 'category-code', 'index': ALL}, 'n_clicks'),
    State({'type': 'category-code', 'index': ALL}, 'children'),
    State('last-clicked-category', 'data')
)
def actualizar_histograma(item_name, item_code, n_clicks, cat_codes, last_clicked):
    ctx = callback_context
    triggered_id = ctx.triggered[0]['prop_id'] if ctx.triggered else 'No ID'
    
    # Si se activa por cambio en el item code
    if 'selected-item-code' in triggered_id and item_code is not None:
        # Generar gráfica por año para el item code seleccionado
        return [dcc.Graph(id='histograma-graph', figure=graficar_item_por_anio(item_code))], last_clicked
    
    # Si se activa por click en categoría
    if 'category-code' in triggered_id:
        index_click = [i for i, click in enumerate(n_clicks or []) if click]
        if not index_click:
            return dash.no_update, last_clicked

        category_code = cat_codes[index_click[0]]

        # Si el mismo botón se vuelve a clicar, reiniciamos a histograma general
        if last_clicked == category_code:
            return [dcc.Graph(id='histograma-graph', figure=graficar_histograma())], None

        # Graficar top 10 productos para nueva categoría
        return [dcc.Graph(id='histograma-graph', figure=graficar_top_productos(category_code))], category_code

    # Para otros casos mantener el estado actual o usar el histograma por defecto
    if not ctx.triggered:
        return [dcc.Graph(id='histograma-graph', figure=graficar_histograma())], last_clicked
    
    return dash.no_update, last_clicked


# Run
if __name__ == '__main__':
    app.run(debug=True)