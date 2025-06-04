import pandas as pd
import plotly.express as px
import plotly.offline as pyo

HIST_WIDTH = 1100
HIST_HEIGHT = 450

def pie_count_chart(count_list):
    count_df = pd.DataFrame(count_list,columns=['type','count'])
    fig = px.pie(count_df, values='count', names='type', hole=.4, color_discrete_sequence=px.colors.sequential.Darkmint)
    fig.update_traces(textposition='outside', textinfo='label+percent')
    fig.update_layout(showlegend=False,
                      width=700,   
                      height=500,
                      font=dict(size=16))
    graph_html = pyo.plot(fig, include_plotlyjs=False, output_type='div')
    return graph_html

def bar_count_chart(count_list):
    watched = [item[1] for item in count_list if item[0] == 'Просмотрено']
    other_count = sum([int(item[1]) for item in count_list if item[0] != 'Просмотрено'])
    if not watched:
        watched = 0
    else: 
        watched = watched[0]
    if not other_count:
        other_count == 0
    data = {
    'category': ['Сравнение','Сравнение','Сравнение'],
    'type': ['','Просмотрено','В списке'],
    'values': [0,watched, other_count],
    }
    df = pd.DataFrame(data)

    fig = px.bar(df, x="values", y="category",color='type', orientation='h',color_discrete_sequence=px.colors.sequential.Darkmint)
    fig.update_layout(
        showlegend=False,  
        title='',          
        xaxis_title='',    
        yaxis_title='',    
        xaxis=dict(showgrid=False, zeroline=False),  
        yaxis=dict(showgrid=False, zeroline=False),   
        plot_bgcolor='rgba(0, 0, 0, 0)',  
        paper_bgcolor='rgba(0, 0, 0, 0)',
        width=800,   
        height=190,
        font=dict(size=16)
    )
    graph_html = pyo.plot(fig, output_type='div')
    return graph_html

def hist_watched_genres(watched):
    genres = watched['genres'].str.split(' ').explode().value_counts()
    genres = genres[~genres.index.str.contains('unk') & ~(genres.index.str.strip() == '')]
    fig = px.bar(genres, color_discrete_sequence=px.colors.sequential.Blugrn)
    fig.update_layout(
            showlegend=False,  
            title='',          
            xaxis_title='',    
            yaxis_title='',    
            width=HIST_WIDTH,   
            height=HIST_HEIGHT,    
            font=dict(size=16)
        )
    graph_html = pyo.plot(fig, output_type='div')
    return graph_html

def hist_watched_type(watched):
    fig = px.bar(watched['type'].value_counts(), color_discrete_sequence=px.colors.sequential.Blugrn)
    fig.update_layout(
            showlegend=False,  
            title='',          
            xaxis_title='',    
            yaxis_title='',    
            width=HIST_WIDTH,   
            height=HIST_HEIGHT,    
            font=dict(size=16)
        )
    graph_html = pyo.plot(fig, output_type='div')
    return graph_html
    
def hist_watched_pegi(watched):
    fig = px.bar(watched['pegi'].value_counts(), color_discrete_sequence=px.colors.sequential.Blugrn)
    fig.update_layout(
            showlegend=False,  
            title='',          
            xaxis_title='',    
            yaxis_title='',    
            width=HIST_WIDTH,   
            height=HIST_HEIGHT,    
            font=dict(size=16)
        )
    graph_html = pyo.plot(fig, output_type='div')
    return graph_html

def hist_watched_studio(watched):
    fig = px.bar(watched['studio'].value_counts().iloc[:15], color_discrete_sequence=px.colors.sequential.Blugrn)
    fig.update_layout(
            showlegend=False,  
            title='',          
            xaxis_title='',    
            yaxis_title='',    
            width=HIST_WIDTH,   
            height=HIST_HEIGHT,   
            font=dict(size=16)
        )
    graph_html = pyo.plot(fig, output_type='div')
    return graph_html
