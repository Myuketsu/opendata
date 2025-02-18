import plotly.graph_objects as go
from matplotlib.patches import Circle
import matplotlib.pyplot as plt
import io
import base64
import seaborn as sns
import folium

def elbow_graph(inertia) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=list(range(1, len(inertia) + 1)), y=inertia, mode='lines+markers', marker=dict(color='blue')))
    fig.update_layout(
        title='Méthode du coude pour un k optimal',
        xaxis_title='Number of clusters',
        yaxis_title='Inertia',
        template='plotly_white',
        height=350,
    )
    
    return fig


def corr_circle(pca, pca_df, df):
    # Create a figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

    # Affiche le cercle de corrélation
    # Cercle de corrélation
    circle = Circle((0, 0), 1, facecolor='none', edgecolor='b')
    ax1.add_patch(circle)

    # Afficher les vecteurs
    for i, (var, component) in enumerate(zip(df.columns[2::], pca.components_.T)):
        ax1.arrow(0, 0, component[0], component[1], color='r', alpha=0.5)
        ax1.text(component[0] * 1.15, component[1] * 1.15, var, color='g', ha='center', va='center')

    ax1.set_xlim(-1, 1)
    ax1.set_ylim(-1, 1)
    ax1.set_xlabel('PC1')
    ax1.set_ylabel('PC2')
    ax1.grid()
    ax1.set_title('Cercle des corrélations')

    colors = ['blue', 'red', 'green', 'purple']

    sns.scatterplot(data=pca_df, x='PC1', y='PC2', hue='Cluster', palette=colors, ax=ax2)
    ax2.set_title('PCA of Barri Data')
    ax2.set_xlabel('Principal Component 1')
    ax2.set_ylabel('Principal Component 2')
    ax2.legend(title='Cluster')
    ax2.grid()

    buf = io.BytesIO() # in-memory files
    plt.savefig(buf, format = "png")
    plt.close()
    data = base64.b64encode(buf.getbuffer()).decode("utf8") # encode to html elements
    buf.close()

    return "data:image/png;base64,{}".format(data)


def socio_economic_map(map_df) -> folium.Map:
    # Créer une carte centrée sur Barcelone
    map = folium.Map(location=[41.3851, 2.1734], zoom_start=12)

    # Define a color map for clusters
    colors = {0: 'red', 1: 'blue', 2: 'green', 3: 'purple'}

    # Add GeoJson layers for each cluster
    for cluster, color in colors.items():
        feature_group = folium.FeatureGroup(name=f'Cluster {cluster}')
        folium.GeoJson(
            map_df[map_df['Cluster'] == cluster],
            style_function=lambda x, color=color: {'fillColor': color, 'color': color, 'weight': 0.5, 'fillOpacity': 0.7},
            tooltip=folium.GeoJsonTooltip(fields=['nom_barri', 'Cluster'], aliases=['Neighborhood', 'Cluster'])
        ).add_to(feature_group)
        feature_group.add_to(map)
    
    return map