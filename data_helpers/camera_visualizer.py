import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.spatial.transform import Rotation as R
import torch
import plotly.graph_objs as go  # new

class CameraPoseVisualizerSlim:
    """
    Adapted from https://github.com/demul/extrinsic2pyramid
    """
    def __init__(self, xlim=[-5, 15], ylim=[0, 20],zlim=[-5, 15]):
        self.fig = plt.figure(figsize=(10, 10), constrained_layout=True)
        self.fig.patch.set_alpha(0)

        self.subfigs = self.fig.subfigures(nrows=1, ncols=1)

        self.ax3d1 = self.subfigs.add_subplot(1, 1, 1, projection='3d', facecolor="none")

        self.ax3d1.set_xlim(xlim)
        self.ax3d1.set_ylim(ylim)
        self.ax3d1.set_zlim(zlim)

        self.ax3d1.set_box_aspect(aspect =(xlim[1]-xlim[0],ylim[1]-ylim[0],zlim[1]-zlim[0]))


        self.intrinsics = np.eye(3)
        self.intrinsics[0, 0] = 237.5
        self.intrinsics[0, 2] = 237.5
        self.intrinsics[1, 1] = 237.5
        self.intrinsics[1, 2] = 237.5


    def extrinsic2pyramidAbs(self, extrinsic, color='r', focal_len_scaled=5, aspect_ratio=0.7):
        vertex_std = np.array([[0, 0, 0, 1],
                               [focal_len_scaled * aspect_ratio, -focal_len_scaled * aspect_ratio, focal_len_scaled, 1],
                               [focal_len_scaled * aspect_ratio, focal_len_scaled * aspect_ratio, focal_len_scaled, 1],
                               [-focal_len_scaled * aspect_ratio, focal_len_scaled * aspect_ratio, focal_len_scaled, 1],
                               [-focal_len_scaled * aspect_ratio, -focal_len_scaled * aspect_ratio, focal_len_scaled, 1]])
        vertex_transformed = vertex_std @ extrinsic.T
        meshes = [[vertex_transformed[0, :-1], vertex_transformed[1][:-1], vertex_transformed[2, :-1]],
                            [vertex_transformed[0, :-1], vertex_transformed[2, :-1], vertex_transformed[3, :-1]],
                            [vertex_transformed[0, :-1], vertex_transformed[3, :-1], vertex_transformed[4, :-1]],
                            [vertex_transformed[0, :-1], vertex_transformed[4, :-1], vertex_transformed[1, :-1]],
                            [vertex_transformed[1, :-1], vertex_transformed[2, :-1], vertex_transformed[3, :-1], vertex_transformed[4, :-1]]]

        self.ax3d1.add_collection3d(
            Poly3DCollection(meshes, facecolors=color, linewidths=0.3, edgecolors=color, alpha=0.35))


    def customize_legend(self):
        list_handle = []
        list_handle.append(Patch(color='c', label='Ground truth'))
        list_handle.append(Patch(color='y', label='Prediction'))

        self.ax3d2.legend(loc='upper left', handles=list_handle)


    def show(self, name='deleteme'):  # saves png 
        plt.savefig(name + '.png', bbox_inches='tight',pad_inches=0) 
    
    
    def plot_interactive(self, name='interactive_plot'):
        """
        Adapted from https://github.com/demul/extrinsic2pyramid/blob/main/demo3.py
        """
        # Collect all traces (meshes) from the 3D plot
        traces = self.ax3d1.collections  # Access the 3D meshes

        layout = go.Layout(
            title="Interactive 3D Camera Pose Visualization",
            scene=dict(
                xaxis=dict(title="X", range=[-5, 15]),
                yaxis=dict(title="Y", range=[0, 20]),
                zaxis=dict(title="Z", range=[-5, 15]),
            ),
            showlegend=True,
        )

        fig = go.Figure(layout=layout)

        # Add each mesh to the Plotly figure
        for trace in traces:
            # Extract vertices and faces from the mesh
            vertices = np.array([np.array(face)[:, :3] for face in trace.get_segments()]).reshape((-1, 3))
            faces = np.array([np.arange(len(vertices))])

            fig.add_trace(go.Mesh3d(
                x=vertices[:, 0], y=vertices[:, 1], z=vertices[:, 2],
                i=faces[:, 0], j=faces[:, 1], k=faces[:, 2],
                opacity=0.35, color=trace.get_facecolor()[0]
            ))

        # Save as html
        fig.write_html()