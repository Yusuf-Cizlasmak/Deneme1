import gym
from gym import spaces
import numpy as np
import plotly.graph_objects as go
import os
import random as rand
import plotly.io as pio

class Bin:
    def __init__(self, width, height, depth):
        """
        width: int (Bin Genişliği)
        height: int (Bin Yüksekliği)
        depth: int (Bin Derinliği)
        boxes: list (Kutuların listesi)
        used_space: np.ndarray (Kutuların yerleştirildiği alan için kullanılan alanın işaretlenmesi için kullanılır.)

        Örneğin : 
        used_space = np.zeros((10, 10, 10), dtype=bool)
        used_space[0:2, 0:2, 0:2] = True
        """
    
        self.width = width
        self.height = height
        self.depth = depth
        self.boxes = []
        self.used_space = np.zeros((width, height, depth), dtype=bool)

class Box:
    def __init__(self, type, width, height, depth):
        self.type = type
        self.width = width
        self.height = height
        self.depth = depth
        self.position = None
        self.volume = width * height * depth
        self.color = None
        self.size = (width, height, depth)

    def set_position(self, x, y, z):
        self.position = (x, y, z)

    def set_color(self, color):
        self.color = color

class BinPackingEnv(gym.Env):
    def __init__(self, bins, boxes, box_colors):
        super(BinPackingEnv, self).__init__()
        
        self.bins = bins
        self.boxes = boxes
        self.box_colors = box_colors
        self.current_box = None
        self.current_bin = None
        
        self.action_space = spaces.Discrete(len(self.bins))  # Number of bins
        self.observation_space = spaces.Box(
            low=0, high=max(max(bin.width, bin.height, bin.depth) for bin in bins),
            shape=(len(self.bins), 3), dtype=np.float32
        )
        
        self.reset()

    def reset(self):
        self.unplaced_boxes = list(self.boxes)
        self.current_box = self.unplaced_boxes.pop() if self.unplaced_boxes else None
        self.state = np.zeros((len(self.bins), 3))
        for i, bin in enumerate(self.bins):
            self.state[i] = [bin.width, bin.height, bin.depth]
        return self.state

    def step(self, action):
        done = False
        reward = 0
        
        if self.current_box and action < len(self.bins):
            bin = self.bins[action]
            x, y, z = self.find_new_position(self.current_box, bin)
            if x is not None:
                self.current_box.set_position(x, y, z)
                bin.boxes.append(self.current_box)
                self.update_used_space(self.current_box, bin, x, y, z)
                reward = self.current_box.volume
                self.current_box = self.unplaced_boxes.pop() if self.unplaced_boxes else None
            else:
                reward = -self.current_box.volume  # Negative reward for invalid placement
        
        if not self.current_box:
            done = True
        
        return self.state, reward, done, {}
    
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

    def render(self, index, mode='human'):
        self.plot_bins(self.bins, self.bins[0].width, self.bins[0].height, self.bins[0].depth, self.box_colors,index=index)
    
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

    def plot_box(self,box, color, figure=None):
        vertices = BinPackingEnv.generate_vertices(box.size, box.position).T
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

    def plot_bins(self,bins, container_width, container_height, container_depth, box_colors, index=0):
        fig = go.Figure()
        for bin in bins:
            for box in bin.boxes:
                color = box_colors[box.type]
                fig = self.plot_box(box, color, fig)

        fig.update_layout(
            scene=dict(
                xaxis=dict(range=[0, container_width], title='Width'),
                yaxis=dict(range=[0, container_height], title='Height'),
                zaxis=dict(range=[0, container_depth], title='Depth'),
                aspectmode='manual',
                aspectratio=dict(x=1, y=1, z=1),
                bgcolor='rgba(0,0,0,1)'
            ),
            title=f"Container: {container_width, container_height, container_depth}<br>USED SPACE: {self.calculate_remaining_volume(bins[0], bins[0].boxes):.2f}%",
            paper_bgcolor='rgba(0,0,0,1)',
            font=dict(color='white')
        )
        
        if not os.path.exists('plots'):
            os.makedirs('plots')
        
        # Save as HTML
        html_path = os.path.join('plots', f'plot_rl{index}.html')
        pio.write_html(fig, file=html_path, auto_open=False)
        
        # Save as static image (PNG)
        png_path = os.path.join('plots', f'plot_rl{index}.png')
        fig.write_image(png_path)
        
        return fig

    def calculate_remaining_volume(self, container, boxes):
        total_volume = container.width * container.height * container.depth
        used_volume = sum(box.width * box.height * box.depth for box in boxes)
        return (used_volume / total_volume) * 100

    def close(self):
        pass

# Define bins and boxes
container_width = 400
container_height = 30
container_depth = 30

num_bins = 1
bins = [Bin(container_width, container_height, container_depth)]

boxes = []

#Senaryo3.csv

for _ in range(100):
    boxes.append(Box(1, 1, 2, 3))

for _ in range(20):
    boxes.append(Box(2, 4, 5, 6))

for _ in range(8):
    boxes.append(Box(3, 22, 23, 24))

for _ in range(8):
    boxes.append(Box(4, 25, 26, 27))

for _ in range(4):
    boxes.append(Box(5, 7, 8, 9))

boxes.append(Box(6, 19, 20, 21))


# Assign colors to box types
box_colors = {}
for k in range(1, len(boxes) + 1):
    box_colors[k] = f'rgb({rand.randint(0, 255)}, {rand.randint(0, 255)}, {rand.randint(0, 255)})'

# Set the color of each box based on its type
for box in boxes:
    box.set_color(box_colors[box.type])

# Create the environment
env = BinPackingEnv(bins, boxes, box_colors)

# Train the RL model using Stable Baselines3
from stable_baselines3 import PPO

model = PPO('MlpPolicy', env, verbose=1)
model.learn(total_timesteps=10000)

# Save the model
model.save("ppo_bin_packing")

# Load the model (if needed)
model = PPO.load("ppo_bin_packing")

# Test the trained model
obs = env.reset()
for _ in range(100):
    action, _states = model.predict(obs, deterministic=True)
    obs, reward, done, info = env.step(action)
    
    if _ % 10 == 0:
        env.render(index=_)

    if done:
        obs = env.reset()
