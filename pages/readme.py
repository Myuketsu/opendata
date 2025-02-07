from dash import register_page, dcc

register_page(__name__, path='/readme', name='Contexte', title='OPENDATA')

def layout():
    with open('README.md', 'r', encoding='utf-8') as f:
        content = f.readlines()
    return dcc.Markdown(content, style={'marginTop': '-28px'})