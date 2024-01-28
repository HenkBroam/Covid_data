import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import panel as pn

pn.extension()

# laad de data in 
file_path = 'covid_patienten_export.tsv'
data_p = pd.read_table(file_path, sep='\t')
data_p['IN_LEVEN_3_MAANDEN'] = data_p['IN_LEVEN_3_MAANDEN'].fillna('ja')

# Hier wordt de scatter plot gemaakt.
scatter_plot_alive = go.Figure()

# 2 variabelen maken met ja of nee patienten 
filtered_data_alive = data_p[data_p["IN_LEVEN_3_MAANDEN"] == "ja"]
filtered_data_dead = data_p[data_p["IN_LEVEN_3_MAANDEN"] == "nee"]

# de plot zelf maken voor de levende patienten
scatter_plot_alive.add_trace(go.Scatter(
    x=filtered_data_alive['LEEFTIJD'],
    y=filtered_data_alive['APACHE_IV_SCORE'],
    mode='markers',
    marker=dict(size=8, color='blue'),
    name='Scatter Plot (Alive after 3 months)'
))

# de plot zelf maken voor de overleden mensen 
scatter_plot_alive.add_trace(go.Scatter(
    x=filtered_data_dead['LEEFTIJD'],
    y=filtered_data_dead['APACHE_IV_SCORE'],
    mode='markers',
    marker=dict(size=8, color='red'),
    name='Scatter Plot (Not alive after 3 months)'
))

# De scatterplot updaten (geprobeerd om deze plot interactief te maken)
scatter_plot_alive.update_layout(
    title='Scatter Plot of APACHE_IV_SCORE vs Age for Patients',
    xaxis_title='Age',
    yaxis_title='APACHE_IV_SCORE',
    showlegend=True,
)

# De andere data inladen 
file_path_meet = 'covid_meetgegevens_export.tsv'
data_meet = pd.read_table(file_path_meet, sep='\t')

# Rename variables
mach_name = "EE_BEADEMINGSMACH"
mach_data = data_meet[mach_name]
voeding_name = "VOEDING_ML24H"
voeding_data = data_meet[voeding_name]

# De line plot samen voegen 
def combined_line_plot(show_combined=True):
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(x=mach_data.index, y=mach_data.values, mode='lines', name=f'Line Graph for {mach_name}'))
    
    if show_combined:
        fig.add_trace(go.Scatter(x=voeding_data.index, y=voeding_data.values, mode='lines', name=f'Line graph for {voeding_name}'))

    fig.update_layout(
        title='Combined Line Plots',
        xaxis_title='Aantal meetmomenten',
        yaxis_title='Aantal kcal',
        showlegend=True,
        height=500,
        width=800
    )
    return fig

# Checkbox maken
show_combined_checkbox = pn.widgets.Checkbox(name="Show Combined Graph", value=True)

# Dropdown menu voor geslacht
gender_dropdown = pn.widgets.Select(name='Select Gender', options=['All', 'Men', 'Women'], value='All')

# call functie van de checkbox
def on_checkbox_change(event):
    combined_plot_pane.object = combined_line_plot(show_combined_checkbox.value)

# Call functie voor het dropdown menu
def on_gender_dropdown_change(event):
    update_bar_plot()

show_combined_checkbox.param.watch(on_checkbox_change, 'value')
gender_dropdown.param.watch(on_gender_dropdown_change, 'value')

# pane maken
combined_plot_pane = pn.pane.Plotly(combined_line_plot(show_combined_checkbox.value))

# Data (nog een keer) inladen voor barplot
file_path_patienten = 'covid_patienten_export.tsv'
data_p = pd.read_table(file_path_patienten, sep='\t')

# barplot maken in deze functie
def plot_bar(column_name, title, weight_value, lengte_value, leeftijd_value, apache_value, gender_value):
    if gender_value == 'All':
        filtered_data = data_p[(data_p['GEWICHT'] >= weight_value) & 
                               (data_p['LENGTE'] >= lengte_value) &
                               (data_p['LEEFTIJD'] >= leeftijd_value) &
                               (data_p['APACHE_IV_SCORE'] >= apache_value)]
    else:
        filtered_data = data_p[(data_p['GEWICHT'] >= weight_value) & 
                               (data_p['LENGTE'] >= lengte_value) &
                               (data_p['LEEFTIJD'] >= leeftijd_value) &
                               (data_p['APACHE_IV_SCORE'] >= apache_value) &
                               (data_p['GESLACHT'] == gender_value.lower())]

    counts = filtered_data[column_name].value_counts(normalize=True) * 100  
    
    # COunter voor totaal aantal patienten 
    total_patients = len(filtered_data)
    
    return px.bar(counts, title=title, labels={'index': 'Category', 'value': 'Percentage'}), total_patients

# De default voor de sliders
initial_weight_value = data_p['GEWICHT'].min()
initial_lengte_value = data_p['LENGTE'].min()
initial_leeftijd_value = data_p['LEEFTIJD'].min()
initial_apache_value = data_p['APACHE_IV_SCORE'].min()

# Bar plot voor"IN_LEVEN_3_MAANDEN"
bar_plot_3_months, total_patients_counter = plot_bar('IN_LEVEN_3_MAANDEN', 'In leven bij de 3 maanden mark', 
                                                     initial_weight_value, initial_lengte_value, initial_leeftijd_value, initial_apache_value, 'All')

# Gewicht slider
weight_slider = pn.widgets.FloatSlider(name='Weight Slider minimaal kilos ', start=data_p['GEWICHT'].min(), end=data_p['GEWICHT'].max(),
                                       step=1, value=initial_weight_value)

# Lengte slider
length_slider = pn.widgets.FloatSlider(name='Length Slider minimale centimeters', start=data_p['LENGTE'].min(), end=data_p['LENGTE'].max(),
                                       step=1, value=initial_lengte_value)

# Leeftijd slider
leeftijd_slider = pn.widgets.FloatSlider(name='Leeftijd Slider minimale jaren', start=data_p['LEEFTIJD'].min(), end=data_p['LEEFTIJD'].max(),
                                       step=1, value=initial_leeftijd_value)

# APACHE iv score  slider
apache_slider = pn.widgets.FloatSlider(name='APACHE Slider minimale score', start=data_p['APACHE_IV_SCORE'].min(), 
                                       end=data_p['APACHE_IV_SCORE'].max(), step=1, 
                                       value=initial_apache_value)

# Counter display weergeven 
total_patients_text = pn.pane.Markdown(f'Total Patients: {total_patients_counter}', style={'font-size': '14pt', 'margin-top': '10px'})

# Call back voor gewicht slider
def on_weight_slider_change(event):
    update_bar_plot()

# Call back voor lengte slider
def on_length_slider_change(event):
    update_bar_plot()

# Call back voor leeftijd slider
def on_leeftijd_slider_change(event):
    update_bar_plot()

# Call voor apache iv score slider
def on_apache_slider_change(event):
    update_bar_plot()

# weergeven de current value voor de slider
weight_slider.param.watch(on_weight_slider_change, 'value')
length_slider.param.watch(on_length_slider_change, 'value')
leeftijd_slider.param.watch(on_leeftijd_slider_change, 'value')
apache_slider.param.watch(on_apache_slider_change, 'value')

# de barplot updaten in deze functie 
def update_bar_plot():
    # drop down menu voor gender maken 
    gender_mapping = {'All': None, 'Man': 'm', 'Vrouw': 'v'}
    gender_value = gender_mapping[gender_dropdown.value]

    # data filteren 
    weights = data_p[(data_p['GEWICHT'] >= weight_slider.value) & 
                     (data_p['LENGTE'] >= length_slider.value) &
                     (data_p['LEEFTIJD'] >= leeftijd_slider.value) &
                     (data_p['APACHE_IV_SCORE'] >= apache_slider.value) &
                     ((data_p['GESLACHT'] == gender_value) | (gender_value is None))]

    # de count maken 
    counts = weights['IN_LEVEN_3_MAANDEN'].value_counts(normalize=True) * 100

    # het updaten van de count
    updated_counts = pd.DataFrame(index=['ja', 'nee'], data={'Percentage': [0, 0]})
    updated_counts.loc[counts.index, 'Percentage'] = counts.values

    # Update van barplot
    bar_plot_3_months.update_traces(x=updated_counts.index, y=updated_counts['Percentage'])
    bar_plot_3_months.update_layout(title='In leven bij de 3 maanden mark', yaxis_title='Percentage')

    # Update van counter van totaal aantal patienten 
    total_patients_text.object = f'Total Patients: {len(weights)}'

# Info tab maken 
info_content = pn.pane.Markdown("""
### Informatie

**EE_BEADEMINGSMACH**: Dit representateerd aantal kcal nodig.
**VOEDING_ML24**: Dit representateerd het aantal kcal binnen gekregen.
**APACHE_IV_SCORE** Dit representateerd de prognose van de patient op de IC, hoe hoger deze score hoe slechter de prognose is voor de patient. 
**IN_LEVEN_3_MAANDEN** Dit representateerd of de patient in leven is of is overleden op de 3 maanden mark. 

""")

# Header
header = pn.pane.Markdown("## My Dashboard", style={'text-align': 'center', 'background-color': '#e6f7ff', 'width': '100%'})

# Spacer voor header
header_spacer = pn.Spacer(width=header.width, height=10, background='#e6f7ff')

# Tabs
tabs = pn.Tabs(
    ("Bar Plots", pn.Row(
        pn.Column(bar_plot_3_months, total_patients_text, width=800),
        pn.Spacer(width=20),
        pn.Column(weight_slider, length_slider, leeftijd_slider, apache_slider, gender_dropdown)
    )),
    ("Scatter Plots", pn.Row(scatter_plot_alive)),
    ("Combined Plots", pn.Column(show_combined_checkbox, combined_plot_pane)),
    ("Info", pn.Column(info_content))
)

# App layout
app = pn.Column(
    header_spacer,
    pn.Row(header, width=header.width),
    tabs
)

app.show()
