import seaborn as sns
from matplotlib import pyplot as plt
from faicons import icon_svg

# Import data from shared.py
from shared import app_dir, KEY_PATH

from shiny import reactive
from shiny.express import input, render, ui
import pandas as pd
import pandas_gbq # Optimiza la conexión entre Pandas y BQ
from google.oauth2 import service_account
PROJECT_ID = "project-0f0167b9-0302-4715-840"




def get_data(query):
    # Cargamos las credenciales desde el JSON
    credentials = service_account.Credentials.from_service_account_file(KEY_PATH)
    
    # Pasamos las credenciales directamente a pandas_gbq
    return pandas_gbq.read_gbq(
        query, 
        project_id=PROJECT_ID, 
        credentials=credentials  # <--- Esto evita que busque el navegador
    )



ui.page_opts(title="", fillable=True)

with ui.layout_column_wrap(width=1):
    ui.markdown(F"""
    ### **Scientific Production in Honduras**  
    """)


with ui.sidebar():

    ui.markdown(
        f"""
        ##### About
        <span style="font-size: 12px;">
        This dashboard displays information on scientific publications in indexed journals, 
        where at least one author is affiliated with one of these institutions:
        
        * Universidad Nacional Autonoma de Honduras
        * Universidad Pedagógica Nacional Francisco Morazán
        * Escuela Agrícola Panamerica del Zamorano
        * Universidad Tecnológica Centroamericana
        </span>
        > **Created by: Lariza Sandoval** 
        
        <span style="font-size: 10px;">last updated: {pd.Timestamp.now().date()}</span>
        """
    )
with ui.layout_column_wrap(fill=False):
    with ui.value_box(showcase=icon_svg("paperclip")):
        "Total of articles"
        
        @render.text
        def count():
            return f"{filtered_df()['doi'].unique().shape[0]:,}"

        @render.text
        def bill_length():
            return f""""""
    with ui.value_box(showcase=icon_svg("book")):
        "Scientific journals"
        
        @render.text
        def total_magazines():
            return f"{filtered_df()['magazine'].unique().shape[0]:,}"


with ui.layout_columns(col_widths=(4,8)):
    with ui.card(full_screen=True):
        ui.card_header("Articles by Institution")
 
        @render.plot
        def length_depth():
            df = filtered_df()
            gender_counts = df['institution'].value_counts()
            total = gender_counts.sum()

            def absolute_value(val):
                # Calculamos el valor entero original
                a = int(round(val/100.*total))
                return f"{a:d}" # Retorna el número como string
            fig, ax = plt.subplots(figsize=(8, 8))

            gender_counts.plot.pie(
                ax=ax,
                autopct=absolute_value, # <--- Aquí usamos nuestra función
                startangle=90,
                colors=sns.color_palette("bright", len(gender_counts)),
                ylabel='',
                textprops={'fontsize': 9, 'fontweight': 'bold', 'color': '#34495e'} # Para que los números se vean claros
            )
            plt.title('', fontsize=15)
            return fig
   
             
    with ui.card(full_screen=True, style="height: 500px;"):
        ui.card_header("Articles by Publication Year")
    
        @render.plot
        def publication_year_graph():
            
            df = filtered_df() # O el nombre de tu función reactiva
            # Agrupamos y contamos únicos
            stats_year = df.groupby('year')['doi'].nunique().reset_index()
            stats_year = stats_year.sort_values('year')
            
            # 2. Configurar la gráfica
            sns.set_theme(style="whitegrid")
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # 3. Dibujar línea con puntos
            sns.lineplot(
                data=stats_year,
                x='year',
                y='doi',
                marker='o',
                linewidth=2.5,
                color="#db9833",
                ax=ax
            )
            
            # 4. Opcional: Rellenar el área bajo la curva para un look más moderno
            ax.fill_between(stats_year['year'], stats_year['doi'], alpha=0.1, color="#cc8511")

            # 5. Agregar etiquetas de valores sobre cada punto
            for x, y in zip(stats_year['year'], stats_year['doi']):
                ax.text(x, y + 0.5, str(int(y)), ha='center', va='bottom', fontweight='bold', color='#34495e')

            # Formatting
            plt.xlabel('Year', fontsize=10)
            plt.ylabel('Number of Articles', fontsize=10)
            #plt.title('Evolution of Unique Publications', loc='left', fontsize=12, fontweight='bold')
            
            # Ajustar los ticks del eje X para que no se amontonen si hay muchos años
            #plt.xticks(rotation=45)
            
            plt.tight_layout()
            return fig 

ui.include_css(app_dir / "styles.css")

@reactive.calc
def filtered_df():
    filt_df = get_data(f"""
                   SELECT  
                   * 
                   FROM `science_p_raw_data.ftc_science_production`
                   """
                )
    return filt_df
