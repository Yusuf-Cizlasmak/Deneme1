import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import random as rand
import os
import pandas as pd 
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import plotly.graph_objects as go
from plotly.offline import plot




# import numpy as np
# import plotly.graph_objects as go
# import os

# def generate_vertices(cuboid_len_edges, cuboid_position):
#     # Generate the list of vertices by adding the lengths of the edges to the coordinates
#     v0 = cuboid_position
#     v0 = np.asarray(v0, dtype=np.int32)
#     v1 = v0 + np.asarray([cuboid_len_edges[0], 0, 0], dtype=np.int32)
#     v2 = v0 + np.asarray([0, cuboid_len_edges[1], 0], dtype=np.int32)
#     v3 = v0 + np.asarray([cuboid_len_edges[0], cuboid_len_edges[1], 0], dtype=np.int32)
#     v4 = v0 + np.asarray([0, 0, cuboid_len_edges[2]], dtype=np.int32)
#     v5 = v1 + np.asarray([0, 0, cuboid_len_edges[2]], dtype=np.int32)
#     v6 = v2 + np.asarray([0, 0, cuboid_len_edges[2]], dtype=np.int32)
#     v7 = v3 + np.asarray([0, 0, cuboid_len_edges[2]], dtype=np.int32)
#     vertices = np.vstack((v0, v1, v2, v3, v4, v5, v6, v7))
#     return vertices

# def plotCubeAtplotly(positions, sizes, colors, **kwargs):
#     data = []
#     for p, s, c in zip(positions, sizes, colors):
#         vertices = generate_vertices(s, p)
#         x, y, z = vertices[:, 0], vertices[:, 1], vertices[:, 2]
        
#         # Add Mesh3d trace for the cube
#         data.append(go.Mesh3d(
#             x=x,
#             y=y,
#             z=z,
#             i=[0, 1, 1, 2, 2, 3, 3, 0, 4, 5, 5, 6, 6, 7, 7, 4, 0, 4, 1, 5, 2, 6, 3, 7],
#             j=[1, 2, 3, 0, 5, 6, 7, 4, 5, 1, 6, 2, 7, 3, 4, 0, 4, 5, 6, 7, 0, 1, 2, 3],
#             k=[2, 3, 0, 1, 6, 7, 4, 5, 1, 0, 6, 5, 2, 1, 7, 6, 4, 0, 5, 4, 6, 5, 7, 6],
#             color=f"rgb({c[0]}, {c[1]}, {c[2]})",
#             opacity=1,
#             flatshading=True,
#             **kwargs
#         ))
        
#         # Add Scatter3d traces for the 12 edges
#         edges = [
#             (0, 1), (1, 2), (2, 3), (3, 0),  # bottom square
#             (4, 5), (5, 6), (6, 7), (7, 4),  # top square
#             (0, 4), (1, 5), (2, 6), (3, 7)  # vertical edges
#         ]
#         for edge in edges:
#             x_edge = [x[edge[0]], x[edge[1]]]
#             y_edge = [y[edge[0]], y[edge[1]]]
#             z_edge = [z[edge[0]], z[edge[1]]]
#             data.append(go.Scatter3d(
#                 x=x_edge,
#                 y=y_edge,
#                 z=z_edge,
#                 mode='lines',
#                 line=dict(color='black', width=2)
#             ))
    
#     return data

# def plotBox3d(boxes, bin):
#     positions = []
#     sizes = []
#     colors = []
#     box_colors = {}
#     for i, box in enumerate(boxes):
#         if box.boxtype not in box_colors:
#             box_colors[box.boxtype] = [np.random.rand(), np.random.rand(), np.random.rand()]

#     for box in boxes:
#         positions.append(box.position)
#         sizes.append(box.size)
#         colors.append(box_colors[box.boxtype])

#     data = plotCubeAtplotly(positions, sizes, colors)
#     layout = go.Layout(
#         scene=dict(
#             xaxis=dict(range=[0, bin.size[0]]),
#             yaxis=dict(range=[0, bin.size[1]]),
#             zaxis=dict(range=[0, bin.size[2]]),
#         ),
#         margin=dict(l=0, r=0, t=0, b=0),
#         paper_bgcolor='rgba(0,0,0,0)',
#         plot_bgcolor='rgba(0,0,0,0)'
#     )
#     fig = go.Figure(data=data, layout=layout)

#     if not os.path.exists('plots'):
#         os.makedirs('plots')

#     fig.write_html(os.path.join('plots', f'plot_{i}.html'))




def calculate_remaining_volume(bin, boxes):
    total_volume = bin.size[0] * bin.size[1] * bin.size[2]
    used_volume = sum(box.size[0] * box.size[1] * box.size[2] for box in boxes)
    
    kalan_hacim =  total_volume - used_volume
    return (used_volume / total_volume) * 100

def cuboid_data(o, size=(1, 1, 1)):
    X = [[[0, 1, 0], [0, 0, 0], [1, 0, 0], [1, 1, 0]],
         [[0, 0, 0], [0, 0, 1], [1, 0, 1], [1, 0, 0]],
         [[1, 0, 1], [1, 0, 0], [1, 1, 0], [1, 1, 1]],
         [[0, 0, 1], [0, 0, 0], [0, 1, 0], [0, 1, 1]],
         [[0, 1, 0], [0, 1, 1], [1, 1, 1], [1, 1, 0]],
         [[0, 1, 1], [0, 0, 1], [1, 0, 1], [1, 1, 1]]]
    X = np.array(X).astype(float)
    for i in range(3):
        X[:, :, i] *= size[i]
    X += np.array(o)
    return X

def plotCubeAt(positions, sizes=None, colors=None, **kwargs):
    if not isinstance(colors, (list, np.ndarray)): colors = ["C0"] * len(positions)
    if not isinstance(sizes, (list, np.ndarray)): sizes = [(1, 1, 1)] * len(positions)
    g = []
    for p, s, c in zip(positions, sizes, colors):
        g.append(cuboid_data(p, size=s))
    return Poly3DCollection(np.concatenate(g), facecolors=np.repeat(colors, 6, axis=0), **kwargs)

def plotBoxes(boxes, bin):
    positions = []
    sizes = []
    colors = []
    patches = []
    boxtypes = []
    box_colors = {}
    for i,box in enumerate(boxes):
        if box.boxtype not in box_colors:
            box_colors[box.boxtype] = [rand.random(), rand.random(), rand.random()]

    for box in boxes:
        positions.append(box.position)
        sizes.append(box.size)
        colors.append(box_colors[box.boxtype])
        if box.boxtype not in boxtypes:
            boxtypes.append(box.boxtype)
            patches.append(mpatches.Patch(color=box_colors[box.boxtype], label=box.boxtype.senario + " Sünger " + box.boxtype.type ))
        
    positions = np.array(positions)
    sizes = np.array(sizes)
    colors = np.array(colors)
    
    fig = plt.figure()
    fig.patch.set_facecolor('#313332')
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor('#313332')

    pc = plotCubeAt(positions, sizes, colors=colors, edgecolor="k")
    ax.add_collection3d(pc)

    ax.set_xlim([0, bin.size[0]])
    ax.set_ylim([0, bin.size[1]])
    ax.set_zlim([0, bin.size[2]])

    ax.set_xlabel('x', fontsize=8)
    ax.set_ylabel('y', fontsize=8)
    ax.set_zlabel('z', fontsize=8)

    plt.title(f"Konteyner: {bin.size[0],bin.size[1],bin.size[2]} \n ALAN KULLANIMI : {calculate_remaining_volume(bin, boxes)}",color='white', fontsize=10)

    ax.legend(handles=patches, facecolor='darkgrey')
    ax.view_init(azim=45)
    ax.set_box_aspect([bin.size[0], bin.size[1]*2, bin.size[2]*2])
    ax.grid(False)

    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
    ax.tick_params(axis='y', labelrotation=60, colors='white')
    ax.tick_params(axis='x', labelrotation=0, colors='white')
    ax.tick_params(axis='z', labelrotation=0, colors='white')

    if not os.path.exists('plots'):
        os.makedirs('plots')
    
    plt.savefig(os.path.join('plots', f'plot_{i}.png'))



    plt.show()







