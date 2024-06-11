import plotly.graph_objects as go
import numpy as np
import random as rand
import os
import plotly.io as pio

def generate_vertices(cuboid_len_edges, cuboid_position):
    """Generates the vertices of a box or container in the correct format to be plotted"""
    v0 = cuboid_position
    v0 = np.asarray(v0, dtype=np.int32)
    v1 = v0 + np.asarray([cuboid_len_edges[0], 0, 0], dtype=np.int32)
    v2 = v0 + np.asarray([0, cuboid_len_edges[1], 0], dtype=np.int32)
    v3 = v0 + np.asarray([cuboid_len_edges[0], cuboid_len_edges[1], 0], dtype=np.int32)
    v4 = v0 + np.asarray([0, 0, cuboid_len_edges[2]], dtype=np.int32)
    v5 = v1 + np.asarray([0, 0, cuboid_len_edges[2]], dtype=np.int32)
    v6 = v2 + np.asarray([0, 0, cuboid_len_edges[2]], dtype=np.int32)
    v7 = v3 + np.asarray([0, 0, cuboid_len_edges[2]], dtype=np.int32)
    vertices = np.vstack((v0, v1, v2, v3, v4, v5, v6, v7))
    return vertices

def plot(box, color, figure=None):
    """Adds the plot of a box to a given figure"""
    vertices = generate_vertices(box.size, box.position).T
    x, y, z = vertices[0, :], vertices[1, :], vertices[2, :]
    i = [1, 2, 5, 6, 1, 4, 3, 6, 1, 7, 0, 6]
    j = [0, 3, 4, 7, 0, 5, 2, 7, 3, 5, 2, 4]
    k = [2, 1, 6, 5, 4, 1, 6, 3, 7, 1, 6, 0]

    edge_pairs = [
        (0, 1), (0, 2), (0, 4), (1, 3), (1, 5), (2, 3), (2, 6), (3, 7),
        (4, 5), (4, 6), (5, 7), (6, 7)
    ]

    if figure is None:
        figure = go.Figure()

    # Plot the box faces
    figure.add_trace(go.Mesh3d(
        x=x, y=y, z=z,
        i=i, j=j, k=k,
        opacity=1, color=color,
        flatshading=True,
        name=f'Box {box.boxtype.type}',
        showlegend=True
    ))

    # Plot the box edges
    for (m, n) in edge_pairs:
        vert_x = np.array([x[m], x[n]])
        vert_y = np.array([y[m], y[n]])
        vert_z = np.array([z[m], z[n]])
        figure.add_trace(go.Scatter3d(
            x=vert_x, y=vert_y, z=vert_z,
            mode="lines", line=dict(color="black", width=2),
            name=f'Edges {box.boxtype}',
            showlegend=False  # Kenarlar için legend gösterilmez
        ))

    return figure

def calculate_remaining_volume(bin, boxes):
    total_volume = bin.size[0] * bin.size[1] * bin.size[2]
    used_volume = sum(box.size[0] * box.size[1] * box.size[2] for box in boxes)
    return (used_volume / total_volume) * 100

def plotBoxes(boxes, bin):
    fig = go.Figure()
    box_colors = {}
    for i, box in enumerate(boxes):
        if box.boxtype not in box_colors:
            box_colors[box.boxtype] = f'rgb({rand.randint(0, 255)}, {rand.randint(0, 255)}, {rand.randint(0, 255)})'
    
    for box in boxes:
        fig = plot(box, box_colors[box.boxtype], fig)
    
    fig.update_layout(
        scene=dict(
            xaxis=dict(range=[0, bin.size[0]], title='x'),
            yaxis=dict(range=[0, bin.size[1]], title='y'),
            zaxis=dict(range=[0, bin.size[2]], title='z'),
            aspectmode='manual',
            aspectratio=dict(x=1, y=1, z=1),
            bgcolor='rgba(0,0,0,1)'
        ),
        title=f"Konteyner: {bin.size[0],bin.size[1],bin.size[2]}<br>ALAN KULLANIMI: {calculate_remaining_volume(bin, boxes):.2f}%",
        paper_bgcolor='rgba(0,0,0,1)',
        font=dict(color='white')
    )
    
    if not os.path.exists('plots'):
        os.makedirs('plots')
    
    return fig
