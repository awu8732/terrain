import time
import numpy as np
from noise import pnoise2
from numba import njit
from pygame.locals import *
from OpenGL.GL import * 
from OpenGL.GLU import *

import configuration as config
import models.terrain
import core.state as state
import utility

class TerrainRenderer:
    """
    Handles terrain generation, mesh creation, and OpenGL rendering.
    
    This class manages the complete terrain pipeline from heightmap generation
    through mesh creation to real-time rendering with lighting calculations.
    """
    
    def __init__(self):
        """Initialize the terrain renderer."""
        self.utility_manager = utility.UtilityManager()
        
    def generate_mesh(self, heightmap):
        """
        Generate 3D mesh vertices and triangle indices from a 2D heightmap.
        
        Creates a triangulated mesh suitable for OpenGL rendering, with optional
        hydraulic erosion simulation applied to the heightmap.
        """
        # Clear previous mesh data
        state.MESH.vertices = []
        state.MESH.indices = []
        
        width, depth = heightmap.shape
        erosion_start_time = time.perf_counter()
        self.utility_manager.reset_erosion_statistics()
        
        # Apply hydraulic erosion if enabled
        if config.SIMULATE_EROSION:
            heightmap, state.STATS.TOTAL_D, state.STATS.TOTAL_E = (
                simulate_hydraulic_erosion_numba(
                    heightmap, 
                    iterations=config.EROSION_ITERATIONS,
                    initial_velocity=config.EROSION_INIT_VELOCITY
                )
            )
            state.STATS.ERO_TIME = (time.perf_counter() - erosion_start_time) * 1000
            self.utility_manager.output_erosion_statistics()
            
        # Generate vertex list from heightmap
        for x in range(width):
            for z in range(depth):
                y = heightmap[x][z] * config.HEIGHTMAP_SCALE
                state.MESH.vertices.append((x, y, z))
                
        # Generate triangle indices for mesh connectivity
        for x in range(width - 1):
            for z in range(depth - 1):
                # Calculate vertex indices for current quad
                top_left = x * depth + z
                top_right = (x + 1) * depth + z
                bottom_left = x * depth + (z + 1)
                bottom_right = (x + 1) * depth + (z + 1)
                
                # Create two triangles per quad
                state.MESH.indices.append((top_left, bottom_left, top_right))
                state.MESH.indices.append((top_right, bottom_left, bottom_right))
    
    def regenerate_terrain(self):
        """
        Generate a new terrain with current configuration parameters.
        
        Creates a new Terrain object, generates the mesh, updates statistics,
        and configures the OpenGL camera view.
        """
        generation_start = time.perf_counter()
        
        # Create new terrain with current parameters
        terrain = models.terrain.Terrain()
        self.generate_mesh(terrain.heightmap)
        
        # Configure camera position based on terrain size
        eye_position = self.utility_manager.get_camera_eye_pos(
            config.HEIGHTMAP_WIDTH, 
            config.HEIGHTMAP_DEPTH, 
            config.ELEVATION_VIEW
        )
        
        # Update mesh statistics
        state.STATS.VERTEX_COUNT = len(state.MESH.vertices)
        state.STATS.TRIANGLE_COUNT = len(state.MESH.indices)
        state.STATS.GEN_TIME = (time.perf_counter() - generation_start) * 1000
        
        # Reset OpenGL model-view matrix and position camera
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(-eye_position[0], -eye_position[1], -eye_position[2])
        
        return terrain.normal_map, terrain.biome_map
    
    def render_terrain(self, normals, biome_map):
        """
        Render the terrain mesh with Blinn-Phong lighting and biome coloring.
        
        Applies lighting calculations to each vertex and renders triangles
        with appropriate colors based on biome information or height-based
        coloring.
        """
        vertices = state.MESH.vertices
        indices = state.MESH.indices
        
        # Calculate lighting intensities for all vertices
        intensities = compute_blinn_phong_intensities_numba(
            np.array(normals),
            config.LIGHTING_L_DIR,
            config.LIGHTING_V_DIR,
            config.LIGHTING_K_AMB,
            config.LIGHTING_K_DIFF,
            config.LIGHTING_K_SPEC,
            config.LIGHTING_SHIN
        )
        
        # Render triangulated mesh
        glBegin(GL_TRIANGLES)
        for triangle in indices:
            for vertex_index in triangle:
                vertex = vertices[vertex_index]
                intensity = intensities[vertex_index]
                
                # Determine base color from biome or height
                if config.SIMULATE_BIOME:
                    base_color = self.utility_manager.get_biome_color_from_vertex(
                        vertex, biome_map
                    )
                else:
                    # Height-based coloring for non-biome mode
                    height_factor = vertex[1]
                    base_color = np.array([
                        0.3 + height_factor * 0.02,
                        0.3 + height_factor * 0.10,
                        0.3
                    ])
                
                # Apply lighting to base color
                shaded_color = np.clip(np.array(base_color) * intensity, 0.0, 1.0)
                
                glColor3f(*shaded_color)
                glVertex3f(*vertex)
        glEnd()


@njit
def compute_blinn_phong_intensities_numba(normals, light_dir, view_dir, 
                                        k_ambient, k_diffuse, k_specular, shininess):
    """
    Compute Blinn-Phong lighting intensities for terrain vertices  
    Args:
        normals (numpy.ndarray): Surface normal vectors for each vertex
        light_dir (numpy.ndarray): Normalized light direction vector
        view_dir (numpy.ndarray): Normalized view direction vector
        k_ambient (float): Ambient reflection coefficient
        k_diffuse (float): Diffuse reflection coefficient
        k_specular (float): Specular reflection coefficient
        shininess (float): Specular shininess exponent
    """
    intensities = np.zeros(normals.shape[0])
    
    # Calculate half-vector for Blinn-Phong model
    half_vec = (light_dir + view_dir)
    half_vec /= np.linalg.norm(half_vec)
    
    for i in range(normals.shape[0]):
        normal = normals[i]
        
        # Calculate dot products for lighting components
        dot_nl = np.dot(normal, light_dir)
        dot_nh = np.dot(normal, half_vec)
        
        # Compute lighting components
        ambient = k_ambient
        diffuse = k_diffuse * np.maximum(dot_nl, 0.0)
        specular = k_specular * (np.maximum(dot_nh, 0.0) ** shininess)
        
        # Combine components and clamp to valid range
        total_intensity = ambient + diffuse + specular
        intensities[i] = np.minimum(1.0, np.maximum(0.0, total_intensity))
        
    return intensities


@njit
def simulate_hydraulic_erosion_numba(heightmap, iterations=1000000, 
                                   initial_velocity=0.0, erosion_radius=3):
    """
    Simulate hydraulic erosion using water droplet physics.
    
    Optimized using Numba JIT compilation for performance. Simulates
    water droplets flowing across the terrain, carrying and depositing
    sediment based on velocity and slope.
    
    Args:
        heightmap (numpy.ndarray): Input terrain heightmap to erode
        iterations (int): Number of water droplets to simulate
        initial_velocity (float): Starting velocity for droplets
        erosion_radius (int): Influence radius for erosion effects
    """
    eroded_map = heightmap.copy()
    width, height = eroded_map.shape
    total_deposited = 0.0
    total_eroded = 0.0
    
    for _ in range(iterations):
        x, y = np.random.randint(0, width), np.random.randint(0, height)
        droplet_velocity = initial_velocity
        droplet_sediment = 0.0
        droplet_water = 1.0
        
        # Simulate droplet lifetime for random droplet
        for _ in range(30):  # Maximum droplet lifetime steps
            x_int, y_int = int(x), int(y)
            
            # Calculate terrain gradient using bilinear interpolation
            if x_int < 0 or x_int >= width - 1 or y_int < 0 or y_int >= height - 1:
                gradient_x = 0.0
                gradient_y = 0.0
            else:
                # Bilinear interpolation for smooth gradients
                x_frac, y_frac = x - x_int, y - y_int
                h00 = eroded_map[x_int, y_int]
                h10 = eroded_map[x_int + 1, y_int]
                h01 = eroded_map[x_int, y_int + 1]
                h11 = eroded_map[x_int + 1, y_int + 1]
                
                gradient_x = (h10 - h00) * (1 - y_frac) + (h11 - h01) * y_frac
                gradient_y = (h01 - h00) * (1 - x_frac) + (h11 - h10) * x_frac

                gradient_x = max(-10.0, min(10.0, gradient_x))
                gradient_y = max(-10.0, min(10.0, gradient_y))

            gradient_magnitude = max(1e-6, np.sqrt(gradient_x**2 + gradient_y**2))
            
            # Stop if no gradient (flat area)
            if gradient_x == 0.0 and gradient_y == 0.0:
                break
                
            # Move droplet down gradient
            x -= gradient_x / gradient_magnitude
            y -= gradient_y / gradient_magnitude

            if x < 0 or x >= width or y < 0 or y >= height:
                break
                
            x_int, y_int = int(x), int(y)
            slope = np.sqrt(gradient_x**2 + gradient_y**2)
            
            # Calculate sediment carrying capacity
            carrying_capacity = droplet_velocity * droplet_water * slope * 0.1
            
            # Deposit or erode based on capacity
            if droplet_sediment > carrying_capacity or eroded_map[x_int, y_int] < 0.0:
                deposit_amount = max(0.0, (droplet_sediment - carrying_capacity) * 0.3)
                eroded_map[x_int, y_int] += deposit_amount
                droplet_sediment -= deposit_amount
                total_deposited += deposit_amount
            else:
                max_erosion = eroded_map[x_int, y_int] * 0.99
                erode_amount = min((carrying_capacity - droplet_sediment) * 0.3, max_erosion)
                eroded_map[x_int, y_int] -= erode_amount
                droplet_sediment += erode_amount
                total_eroded += erode_amount

            droplet_velocity = max(0.0, droplet_velocity + slope - 0.1)
            droplet_water *= 0.99  # Evaporation
    
    return eroded_map, total_deposited, total_eroded