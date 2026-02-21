#!/usr/bin/env python3
"""
UNIVERSE BOOTSTRAP SIMULATION - Frame Capture Version
Saves key frames showing the bootstrap process
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from scipy.ndimage import gaussian_filter

# Constants
GRID_SIZE = 128
T_INITIAL = 100.0
T_CRITICAL = 10.0
T_FINAL = 0.1
COOLING_RATE = 8.0  # Fast cooling to hit bootstrap for sure
XI_CRITICAL = 8.0  # Will definitely hit this!
NOISE_AMPLITUDE = 1.0

class UniverseBootstrap:
    """Simulate universe bootstrap from pure potential"""
    
    def __init__(self, size=GRID_SIZE):
        self.size = size
        self.field = np.random.randn(size, size) * 0.1
        self.temperature = T_INITIAL
        self.time = 0
        self.bootstrapped = False
        self.correlation_length = self.calculate_xi(self.temperature)
        
    def calculate_xi(self, T):
        """Correlation length: xi ~ 1/T"""
        return 10.0 / (T + 0.1)
    
    def generate_correlated_noise(self, xi):
        """Generate noise with correlation length xi"""
        noise = np.random.randn(self.size, self.size)
        sigma = xi / 3.0
        correlated = gaussian_filter(noise, sigma=sigma, mode='wrap')
        return correlated * NOISE_AMPLITUDE
    
    def update_field_pre_bootstrap(self):
        """Pre-bootstrap: pure fluctuations"""
        noise = self.generate_correlated_noise(self.correlation_length)
        self.field = self.field * 0.95 + noise * 0.2
        
    def update_field_post_bootstrap(self):
        """Post-bootstrap: observation maintains structure"""
        field_padded = np.pad(self.field, 1, mode='wrap')
        laplacian = (
            field_padded[:-2, 1:-1] + field_padded[2:, 1:-1] +
            field_padded[1:-1, :-2] + field_padded[1:-1, 2:] -
            4 * self.field
        )
        
        noise = self.generate_correlated_noise(self.correlation_length) * 0.05
        self.field += 0.1 * laplacian - 0.05 * self.field**3 + noise
        
    def step(self):
        """Single simulation step"""
        if self.temperature > T_FINAL:
            self.temperature -= COOLING_RATE * 0.01
        
        self.correlation_length = self.calculate_xi(self.temperature)
        
        if not self.bootstrapped and self.correlation_length >= XI_CRITICAL:
            self.bootstrapped = True
            return True  # Signal bootstrap happened
        
        if self.bootstrapped:
            self.update_field_post_bootstrap()
        else:
            self.update_field_pre_bootstrap()
        
        self.time += 1
        return False

def save_frame(universe, filename, frame_num):
    """Save a single frame"""
    fig = plt.figure(figsize=(14, 6))
    
    # Field visualization
    ax_field = plt.subplot(1, 2, 1)
    field_plot = ax_field.imshow(universe.field, cmap='twilight', vmin=-2, vmax=2)
    ax_field.axis('off')
    plt.colorbar(field_plot, ax=ax_field, fraction=0.046, pad=0.04)
    
    # Status panel
    ax_status = plt.subplot(1, 2, 2)
    ax_status.set_xlim(0, 10)
    ax_status.set_ylim(0, 10)
    ax_status.axis('off')
    
    # Status info
    y_pos = 9
    ax_status.text(1, y_pos, f'Frame: {frame_num}', fontsize=12); y_pos -= 0.8
    ax_status.text(1, y_pos, f'Time: {universe.time} steps', fontsize=12); y_pos -= 0.8
    ax_status.text(1, y_pos, f'Temperature: {universe.temperature:.2f}', fontsize=12); y_pos -= 0.8
    ax_status.text(1, y_pos, f'Correlation ξ: {universe.correlation_length:.2f}', fontsize=12); y_pos -= 1.2
    
    # Phase status
    if universe.bootstrapped:
        ax_status.text(1, y_pos, '⚡ OBSERVATION ACTIVE', fontsize=14, 
                      fontweight='bold', color='green'); y_pos -= 1
        ax_status.text(1, y_pos, 'Reality stabilized.\nStructures persist.\nObservation maintains existence.',
                      fontsize=11, style='italic', color='green')
        title_color = 'green'
        title_suffix = 'POST-BOOTSTRAP'
    else:
        if universe.correlation_length > XI_CRITICAL * 0.7:
            ax_status.text(1, y_pos, '⚠️  APPROACHING CRITICAL', fontsize=14,
                          fontweight='bold', color='orange'); y_pos -= 1
            ax_status.text(1, y_pos, 'Correlation length growing...\nBootstrap imminent.',
                          fontsize=11, style='italic', color='orange')
            title_color = 'orange'
        else:
            ax_status.text(1, y_pos, '❄️  PRE-BOOTSTRAP', fontsize=14,
                          fontweight='bold', color='blue'); y_pos -= 1
            ax_status.text(1, y_pos, 'Pure potential.\nRandom fluctuations.\nNo stable structure.',
                          fontsize=11, style='italic', color='blue')
            title_color = 'blue'
        title_suffix = 'PRE-BOOTSTRAP'
    
    ax_field.set_title(f'Quantum Field - {title_suffix}',
                      fontsize=14, fontweight='bold', color=title_color)
    
    # Progress bars
    y_bar = 2.5
    # Temperature
    temp_bar_bg = patches.Rectangle((1, y_bar), 7, 0.3,
                                     linewidth=1, edgecolor='black', facecolor='lightgray')
    temp_fraction = (T_INITIAL - universe.temperature) / (T_INITIAL - T_FINAL)
    temp_bar = patches.Rectangle((1, y_bar), 7 * temp_fraction, 0.3,
                                  linewidth=0, facecolor='orangered')
    ax_status.add_patch(temp_bar_bg)
    ax_status.add_patch(temp_bar)
    ax_status.text(0.5, y_bar + 0.15, 'T:', fontsize=10, ha='right', va='center')
    
    # Correlation length
    y_bar = 1.5
    xi_bar_bg = patches.Rectangle((1, y_bar), 7, 0.3,
                                   linewidth=1, edgecolor='black', facecolor='lightgray')
    xi_fraction = min(universe.correlation_length / (XI_CRITICAL * 1.5), 1.0)
    xi_color = 'lime' if universe.correlation_length >= XI_CRITICAL else \
               'yellow' if universe.correlation_length > XI_CRITICAL * 0.7 else 'dodgerblue'
    xi_bar = patches.Rectangle((1, y_bar), 7 * xi_fraction, 0.3,
                                linewidth=0, facecolor=xi_color)
    ax_status.add_patch(xi_bar_bg)
    ax_status.add_patch(xi_bar)
    ax_status.text(0.5, y_bar + 0.15, 'ξ:', fontsize=10, ha='right', va='center')
    
    plt.suptitle('UNIVERSE BOOTSTRAP SIMULATION\nWatching Observation Emerge from Pure Potential',
                 fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    plt.savefig(filename, dpi=120, bbox_inches='tight')
    plt.close()

def run_simulation():
    """Run simulation and save key frames"""
    print("="*70)
    print("UNIVERSE BOOTSTRAP SIMULATION")
    print("Based on Solvency Field Theory - Bootstrap Mechanism")
    print("="*70)
    print()
    
    universe = UniverseBootstrap()
    
    # Frames to capture
    frames_to_save = [0, 200, 400, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000, 2200, 2400, 2600, 2800]
    saved_frames = []
    frame_count = 0
    bootstrap_frame = None
    
    print("Running simulation...")
    print(f"Initial: T={universe.temperature:.1f}, ξ={universe.correlation_length:.2f}")
    print()
    
    for step in range(3000):  # Run longer!
        bootstrapped = universe.step()
        
        if bootstrapped:
            bootstrap_frame = step
            print(f"🔥 BOOTSTRAP at step {step}!")
            print(f"   T = {universe.temperature:.2f}")
            print(f"   ξ = {universe.correlation_length:.2f}")
            print(f"   ⚡ OBSERVATION TURNS ON")
            print()
            # Save bootstrap moment
            filename = f'/home/claude/frame_bootstrap.png'
            save_frame(universe, filename, step)
            saved_frames.append(('BOOTSTRAP', filename))
        
        if step in frames_to_save:
            filename = f'/home/claude/frame_{step:04d}.png'
            save_frame(universe, filename, step)
            saved_frames.append((step, filename))
            frame_count += 1
            
            status = "POST-BOOTSTRAP ⚡" if universe.bootstrapped else \
                    "APPROACHING" if universe.correlation_length > XI_CRITICAL * 0.7 else \
                    "PRE-BOOTSTRAP"
            print(f"Frame {step:4d}: T={universe.temperature:6.2f}, " +
                  f"ξ={universe.correlation_length:6.2f} [{status}]")
    
    print()
    print(f"Final: T={universe.temperature:.2f}, ξ={universe.correlation_length:.2f}")
    print()
    print("="*70)
    print(f"Simulation complete! Saved {len(saved_frames)} frames")
    print()
    print("Key frames:")
    for label, filename in saved_frames:
        print(f"  {str(label):12s}: {filename}")
    print("="*70)
    
    return saved_frames

if __name__ == '__main__':
    try:
        frames = run_simulation()
        print()
        print("✓ SUCCESS! Frames saved.")
        print()
        print("The simulation shows:")
        print("  • Pre-bootstrap: Random fluctuations, no structure")
        print("  • Bootstrap moment: When ξ reaches critical threshold")
        print("  • Post-bootstrap: Stable patterns emerge and persist")
        print()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
