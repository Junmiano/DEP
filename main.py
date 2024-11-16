import streamlit as st  # Import the streamlit library for creating web apps
import openpyxl
import pandas as pd  # Import the pandas library for data manipulation
import plotly.express as px  # Import plotly.express for creating plots
import plotly.graph_objects as go
from   scipy.stats import f_oneway
import os

# Set page configuration
st.set_page_config(
    page_title="Foreign Spouse EDA",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="auto")

# Apply custom CSS for theme
st.markdown(
    """
    <style>
    .css-18e3th9 {
        background-color: #00b4d8;
    }
    .css-1d391kg {
        background-color: #FFFFFF;
    }
    .css-1d391kg .css-1v3fvcr {
        background-color: #F0F2F6;
    }
    .css-1d391kg .css-1v3fvcr .css-1v3fvcr {
        color: #31333F;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Your Streamlit app code here
st.title("Foreign Spouse Exploratory Data analysis")
st.caption("NUMBER OF FILIPINO SPOUSES AND OTHER PARTNERS OF FOREIGN NATIONALS BY MAJOR COUNTRY: 1989 - 2022")

main_container =  st.container(border=True)
with main_container:
    # Load the Excel file into a DataFrame
    excel_file = 'data\FS-1989-2022-by-MAJORCOUNTRY.xlsx'
    df = pd.read_excel(excel_file, usecols='A:N', header=2, nrows=34, engine='openpyxl)

    # filling NaN values with 0
    df['% Change'] = df['% Change'].fillna(0)

    # Rename the YEAR Column name
    df = df.rename(columns={'YEAR': 'Year'})

    # Get the number of results after applying the mask
    profile = df.describe()
    profile_tranposed = profile.transpose()

    # Display the number of available results
    profile_tranposed.iloc[0:0].reset_index(drop=True)

    st.html('<h3>Data Analysis Process</h3>')
    
    dataset_container = st.container()
    with dataset_container:
        dataset_expander = st.expander("Dataset",expanded=False,icon=":material/database:")
        with dataset_expander:
            # Display a Dataframe
            dataset_tab = st.tabs(["Dataset Source", "Dataset Profile"])
            with dataset_tab[0]:
                st.dataframe(df.style.highlight_max(axis=0), use_container_width=True)
            with dataset_tab[1]:
                st.dataframe(profile_tranposed.style.highlight_max(axis=0), use_container_width=True)

        yr = df['Year'].unique().tolist()
        # Get the list of country names by excluding specific columns
        country_names = [col for col in df.columns if col not in ['TOTAL', 'Year', '% Change']]
        
        chart_expander = st.expander("Chart Parameters",expanded=False,icon=":material/tune:")
        with chart_expander:

            # Create a slider for selecting a range of years
            yr_selection = st.slider('Year:', min_value=min(yr), max_value=max(yr), value=(min(yr), max(yr)))

            # Create a multiselect for selecting countries
            country_selection = st.multiselect('Select Country:', country_names, default=country_names)

        # Create a mask to filter the DataFrame based on the selected years and countries
        mask = (df['Year'].between(*yr_selection)) & (df[country_selection].any(axis=1))

        # Group the filtered DataFrame by 'Year' and sum the selected countries' columns
        df_grouped = df[mask].groupby(by=['Year']).sum()[country_selection]
        df_grouped = df_grouped.reset_index()

        # List of columns to drop 
        columns_to_drop = ['TOTAL', '% Change'] 
        
        # Drop the specified columns 
        df = df.drop(columns=columns_to_drop)

        # Reshape the DataFrame for plotting
        df_melted = df_grouped.melt(id_vars=['Year'], value_vars=country_selection, var_name='Country', value_name='Count')

        # Replace all NaN values with 0 
        df_melted.fillna(0, inplace=True)

        # Convert 'Year' to string
        df_melted['Year'] = df_melted['Year'].astype(str)
        
        # Create bar chart
        bar_chart = px.bar(df_melted,
                    x='Year',
                    y='Count',
                    text='Count',
                    color='Country',
                    color_discrete_sequence=px.colors.qualitative.Plotly,
                    template='plotly_white')

        # Add a title to the chart
        bar_chart.update_layout(title=f'Foreign Spouse Comparison by Country {min(yr_selection)} - {max(yr_selection)}')
        
        line_chart = px.line(df_melted,
                        x='Year',
                        y='Count',
                        color='Country',
                        hover_data={'Country': True, 'Count': True},  # Add hover text
                        color_discrete_sequence=px.colors.qualitative.Plotly,
                        template='plotly_white')

        line_chart.update_traces(
                hoverlabel=dict(
                    bgcolor="#90e0ef",  # Background color
                    font_size=14,       # Font size
                    font_color="#0077b6",
                    font_family="Calibri",  # Font family
                    namelength=-1     # Prevents truncation of long names
                )
        )       

        # Update layout to make the bars non-stacked
        line_chart.update_layout(title=f'Foreign Spouse Trend by Country {min(yr_selection)} - {max(yr_selection)}')
        pie_chart = px.pie(df_melted,
                    title=f'Distribution of Foreign Spouses {min(yr_selection)} - {max(yr_selection)}',
                    values='Count',
                    names='Country')
                
        chart_expander = st.expander("Visualization",expanded=False,icon=":material/key_visualizer:")
        with chart_expander:
            chart_tab = st.tabs(["Trends Chart", 
                                 "Comparison Chart", 
                                 "Distribution Chart", 
                                 "Heatmap",
                                 "Scatter",
                                 "Boxplot",
                                 "ANOVA"
                                 ])
            with chart_tab[0]:
                st.plotly_chart(line_chart, use_container_width=True)
            with chart_tab[1]:
                st.plotly_chart(bar_chart,use_container_width=True)
            with chart_tab[2]:
                st.plotly_chart(pie_chart, use_container_width=True)
            with chart_tab[3]:
                
                heatmap_pivot_df = df_melted.pivot(index='Country', columns='Year', values='Count')

                # Fill NaN values with 0
                heatmap_pivot_df = heatmap_pivot_df.fillna(0)
                heatmap_pivot_df.columns = heatmap_pivot_df.columns.str.strip()
                
                heatmap_fig = go.Figure(data=go.Heatmap(
                                z=heatmap_pivot_df.values,
                                x=heatmap_pivot_df.columns,
                                y=heatmap_pivot_df.index,
                                colorscale='Viridis'))

                # Update layout for better visualization
                heatmap_fig.update_layout(
                    title=f'Heatmap of Count by Year and Country {min(yr_selection)} - {max(yr_selection)}',
                    xaxis_title='Year',
                    yaxis_title='Country'
                )
                st.plotly_chart(heatmap_fig, use_container_width=True)
            with chart_tab[4]:
                scatter_plot_df = df_melted.pivot(index='Country', columns='Year', values='Count')


                # Flatten the pivoted DataFrame
                scatter_flattened_df = scatter_plot_df.reset_index().melt(id_vars='Country', var_name='Year', value_name='Count')

                # Create the scatter plot
                scatter_fig = go.Figure()

                for country in scatter_flattened_df['Country'].unique():
                    country_data = scatter_flattened_df[scatter_flattened_df['Country'] == country]
                    scatter_fig.add_trace(go.Scatter(
                        x=country_data['Year'],
                        y=country_data['Count'],
                        mode='markers',
                        name=country
                    ))

                # Update layout for better visualization
                scatter_fig.update_layout(
                    title=f'Scatter Plot of Count by Year and Country {min(yr_selection)} - {max(yr_selection)}',
                    xaxis_title='Year',
                    yaxis_title='Count'
                )
                st.plotly_chart(scatter_fig, use_container_width=True)
            with chart_tab[5]:
                
                # Pivot the DataFrame
                boxplot_df = df_melted.pivot(index='Year', columns='Country', values='Count')

                # Fill NaN values with 0
                boxplot_df = boxplot_df.fillna(0)
                                # Fill NaN values with 0
                boxplot_df = boxplot_df.fillna(0)
                boxplot_df.columns = boxplot_df.columns.str.strip()


                # Flatten the pivoted DataFrame
                boxplot_flattened_df = boxplot_df.reset_index().melt(id_vars='Year', var_name='Country', value_name='Count')

                # Create the box plot
                box_fig = go.Figure()

                for country in boxplot_flattened_df['Country'].unique():
                    country_data = boxplot_flattened_df[boxplot_flattened_df['Country'] == country]
                    box_fig.add_trace(go.Box(
                        y=country_data['Count'],
                        x=country_data['Year'].astype(str),  # Convert Year to string for better labeling
                        name=country,
                        boxmean=True  # Display mean in the box plot
                    ))

                # Update layout for better visualization
                box_fig.update_layout(
                    title=f'Box Plot of Count by Year and Country {min(yr_selection)} - {max(yr_selection)}',
                    xaxis_title='Year',
                    yaxis_title='Count'
                )

                # Display the box plot using Streamlit
                st.plotly_chart(box_fig, use_container_width=True) 
            with chart_tab[6]:

                anova_df = df_melted.pivot(index='Year', columns='Country', values='Count')

                # Fill NaN values with 0
                boxplot_df = boxplot_df.fillna(0)

                # Strip any leading/trailing spaces from column names
                anova_df.columns = anova_df.columns.str.strip()

                # Flatten the pivoted DataFrame
                boxplot_flattened_df = boxplot_df.reset_index().melt(id_vars='Year', var_name='Country', value_name='Count')

                st.dataframe(boxplot_flattened_df, use_container_width=True, selection_mode="multi-row")

                # Perform ANOVA
                try:
                    anova_result = f_oneway(
                        anova_df[anova_df['Country'] == 'USA']['Count'],
                        anova_df[anova_df['Country'] == 'Canada']['Count']
                    )
                    # Create the box plot
                    box_fig = go.Figure()

                except KeyError as e:

                    for country in boxplot_flattened_df['Country'].unique():
                        country_data = boxplot_flattened_df[boxplot_flattened_df['Country'] == country]
                        box_fig.add_trace(go.Box(
                        y=country_data['Count'],
                        x=country_data['Year'].astype(str),  # Convert Year to string for better labeling
                        name=country,
                        boxmean=True  # Display mean in the box plot
                    ))
                    
                    # Update layout for better visualization
                    box_fig.update_layout(
                        title=f'Box Plot of Count by Year and Country {min(yr_selection)} - {max(yr_selection)}',
                        xaxis_title='Year',
                        yaxis_title='Count'
                    )

                # Display the box plot using Streamlit
                st.plotly_chart(box_fig, use_container_width=True)
