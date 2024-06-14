import time
import random
import random as rand
import os
import numpy as np

from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import pandas as pd

import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.io as pio

from simanneal import Annealer



def SA_algorithm(data):


    class Bin1:
        def __init__(self, width, height, depth):
            self.width = width
            self.height = height
            self.depth = depth
            self.boxes = []
            self.used_space = np.zeros((width, height, depth), dtype=bool)
    
    class Box1:
        def __init__(self, type, width, height, depth,senario,):
            self.type = type
            self.width = width
            self.height = height
            self.depth = depth
            self.senario = senario
            
            self.position = None
            self.volume = width * height * depth
            self.color = None
            self.size = (width, height, depth)
    
        def set_position(self, x, y, z):
            self.position = (x, y, z)
    
        def set_color(self, color):
            self.color = color
    
    class BinPackingProblem(Annealer):
        def __init__(self, bins, boxes):
            self.bins = bins
            self.boxes = boxes
            self.unplaced_boxes = []
            self.state = self.initial_state()
            super(BinPackingProblem, self).__init__(self.state)
    
        def initial_state(self):
            state = []
            bins = list(self.bins)
            sorted_boxes = sorted(self.boxes, key=lambda box: box.volume, reverse=True)
            for box in sorted_boxes:
                placed = False
                for bin in bins:
                    x, y, z = self.find_new_position(box, bin)
                    if x is not None:
                        state.append((box, bin, x, y, z))
                        bin.boxes.append(box)
                        box.set_position(x, y, z)
                        self.update_used_space(box, bin, x, y, z)
                        placed = True
                        break
                if not placed:
                    self.unplaced_boxes.append(box)
            return state
    
        def find_new_position(self, box, bin):
            for x in range(bin.width - box.width + 1):
                for y in range(bin.height - box.height + 1):
                    for z in range(bin.depth - box.depth + 1):
                        if self.can_fit_in_bin(box, bin, x, y, z):
                            return x, y, z
            return None, None, None
    
        def can_fit_in_bin(self, box, bin, x, y, z):
            for i in range(x, x + box.width):
                for j in range(y, y + box.height):
                    for k in range(z, z + box.depth):
                        if bin.used_space[i][j][k]:
                            return False
            return True
    
        def update_used_space(self, box, bin, x, y, z):
            for i in range(x, x + box.width):
                for j in range(y, y + box.height):
                    for k in range(z, z + box.depth):
                        bin.used_space[i][j][k] = True
    
        def move(self):
            max_volume_box = max(self.state, key=lambda item: item[0].volume)
            box, src_bin, x, y, z = max_volume_box
            dest_bin = random.choice(self.bins)
            if src_bin == dest_bin:
                new_x, new_y, new_z = self.find_new_position(box, dest_bin)
                if new_x is not None:
                    self.state.remove((box, src_bin, x, y, z))
                    dest_bin.boxes.append(box)
                    box.set_position(new_x, new_y, new_z)
                    self.state.append((box, dest_bin, new_x, new_y, new_z))
                    self.update_used_space(box, dest_bin, new_x, new_y, new_z)
    
        def energy(self):
            total_wasted_space = sum(
                (bin.width * bin.height * bin.depth) - sum(box.width * box.height * box.depth for box in bin.boxes)
                for bin in self.bins
            )
            return total_wasted_space
    
    def generate_vertices(cuboid_len_edges, cuboid_position):
        v0 = np.asarray(cuboid_position, dtype=np.int32)
        v1 = v0 + np.asarray([cuboid_len_edges[0], 0, 0], dtype=np.int32)
        v2 = v0 + np.asarray([0, cuboid_len_edges[1], 0], dtype=np.int32)
        v3 = v0 + np.asarray([cuboid_len_edges[0], cuboid_len_edges[1], 0], dtype=np.int32)
        v4 = v0 + np.asarray([0, 0, cuboid_len_edges[2]], dtype=np.int32)
        v5 = v1 + np.asarray([0, 0, cuboid_len_edges[2]], dtype=np.int32)
        v6 = v2 + np.asarray([0, 0, cuboid_len_edges[2]], dtype=np.int32)
        v7 = v3 + np.asarray([0, 0, cuboid_len_edges[2]], dtype=np.int32)
        vertices = np.vstack((v0, v1, v2, v3, v4, v5, v6, v7))
        return vertices
    
    def plot_box(box, color, figure=None):
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
            opacity=0.5, color=color,
            flatshading=True,
            name=f'Box of type {box.type}',
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
                showlegend=False  # Kenarlar için legend gösterilmez
            ))
        return figure
    
    def calculate_remaining_volume(container, boxes):
        total_volume = container.width * container.height * container.depth
        used_volume = sum(box.width * box.height * box.depth for box in boxes)
        return (used_volume / total_volume) * 100
    
    def plot_bins(bins, container_width, container_height, container_depth, box_colors):
        fig = go.Figure()
        for bin in bins:
            for box in bin.boxes:
                color = box_colors[box.type]
                fig = plot_box(box, color, fig)
        fig.update_layout(
            scene=dict(
                xaxis=dict(range=[0, container_width], title='Width'),
                yaxis=dict(range=[0, container_height], title='Height'),
                zaxis=dict(range=[0, container_depth], title='Depth'),
                aspectmode='manual',
                aspectratio=dict(x=1, y=1, z=1),
                bgcolor='rgba(0,0,0,1)'
            ),
            title=f"Container: {container_width, container_height, container_depth}<br>USED SPACE: {calculate_remaining_volume(bins[0], bins[0].boxes):.2f}%",
            paper_bgcolor='rgba(0,0,0,1)',
            font=dict(color='white')
        )
        
        if not os.path.exists('plots'):
            os.makedirs('plots')
        
        # Save as HTML
        html_path = os.path.join('plots', 'plot.html')
        pio.write_html(fig, file=html_path, auto_open=False)
        
        # Save as static image (PNG)
        png_path = os.path.join('plots', 'plot.png')
        fig.write_image(png_path)
        
        
        return fig, problem.unplaced_boxes
    
    if __name__ == '__main__':
    
        data=pd.read_csv("senaryo_1.csv")
        container_width = 330
        container_height = 30
        container_depth = 30
        num_bins = 1
        bins = [Bin1(container_width, container_height, container_depth)]
        boxes = []
        for i in range(len(data)):
            for j in range(data['Miktar'][i]):
                boxes.append(Box1(i+1, int(data['X'][i] *0.1)  , int(data['Y'][i]*0.1) , int(data['Z'][i]*0.1) ,data['Senaryo'][i]))
        # Assign colors to box types
        box_colors = {}
        for k in range(1, len(boxes) + 1):
            box_colors[k] = f'rgb({rand.randint(0, 255)}, {rand.randint(0, 255)}, {rand.randint(0, 255)})'
        # Set the color of each box based on its type
        for box in boxes:
            box.set_color(box_colors[box.type])
        # Simulated Annealing
        problem = BinPackingProblem(bins, boxes)
        problem.steps = 50
        state, energy = problem.anneal()  # ilgili kütüphaneye problemi verip, en düşük enerji seviyesini istiyoruz.
        print("\nSimulated Annealing Best Solution:")
        fig= plot_bins(bins,container_width,container_height,container_depth,box_colors)
        
        
        return fig , problem.unplaced_boxes

fig, unplaced_boxes = SA_algorithm("senaryo_1.csv")

fig[0].show()
print([box.type for box in unplaced_boxes])
