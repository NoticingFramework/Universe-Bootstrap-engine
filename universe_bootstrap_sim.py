#!/usr/bin/env python3
"""
UNIVERSE BOOTSTRAP SIMULATION
Watching observation emerge from pure potential

Shows:
- Pre-bootstrap: Pure quantum fluctuations (t < 1 second)
- Bootstrap transition: Correlation length reaches critical threshold
- Post-bootstrap: Observation turns on, structure stabilizes

Based on Solvency Field Theory framework
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.patches as patches

# Constants (in simulation units)
GRID_SIZE = 128
T_INITIAL = 100.0  # Initial temperature (hot)
T_CRITICAL = 10.0  # Critical temperature for bootstrap
T_FINAL = 1.0      # Final temperature (cool)
COOLING_RATE = 0.5 # How fast temperature drops

XI_CRITICAL = 10.0  # Critical correlation length (in grid units)

# Simulation parameters
STEPS_PER_FRAME = 5
NOISE_AMPLITUDE = 1.0

class UniverseBootstrap:
    """Simulate universe bootstrap from pure potential"""
    
    def __init__(self, size=GRID_SIZE):
        self.size = size
        self.field = np.random.randn(size, size) * 0.1  # Initial quantum fluctuations
        self.temperature = T_INITIAL
        self.time = 0
        self.bootstrapped = False
        self.correlation_length = self.calculate_xi(self.temperature)
        
        # For tracking
        self.temp_history = [T_INITIAL]
        self.xi_history = [self.correlation_length]
        
    def calculate_xi(self, T):
        """Correlation length: xi ~ 1/T (simplified)"""
        return 10.0 / (T + 0.1)  # Avoid division by zero
    
    def generate_correlated_noise(self, xi):
        """Generate noise with correlation length xi"""
        # Start with white noise
        noise = np.random.randn(self.size, self.size)
        
        # Apply Gaussian filter to create correlations
        # Correlation length controlled by filter width
        from scipy.ndimage import gaussian_filter
        sigma = xi / 3.0  # Convert correlation length to Gaussian sigma
        correlated = gaussian_filter(noise, sigma=sigma, mode='wrap')
        
        return correlated * NOISE_AMPLITUDE
    
    def update_field_pre_bootstrap(self):
        """Field evolution before bootstrap - pure fluctuations"""
        # Generate noise with current correlation length
        noise = self.generate_correlated_noise(self.correlation_length)
        
        # Field evolves with damping and noise
        # No stable structure - fluctuations dominate
        self.field = self.field * 0.95 + noise * 0.2
        
    def update_field_post_bootstrap(self):
        """Field evolution after bootstrap - observation maintains structure"""
        # Laplacian (local interactions)
        field_padded = np.pad(self.field, 1, mode='wrap')
        laplacian = (
            field_padded[:-2, 1:-1] + field_padded[2:, 1:-1] +
            field_padded[1:-1, :-2] + field_padded[1:-1, 2:] -
            4 * self.field
        )
        
        # With observation active, structure stabilizes
        # Field equation with small noise
        noise = self.generate_correlated_noise(self.correlation_length) * 0.05
        
        # Evolution: diffusion + self-interaction + noise
        # This creates and maintains stable structures
        self.field += 0.1 * laplacian - 0.05 * self.field**3 + noise
        
    def step(self):
        """Single simulation step"""
        # Cool the universe
        if self.temperature > T_FINAL:
            self.temperature -= COOLING_RATE * 0.01
        
        # Update correlation length
        self.correlation_length = self.calculate_xi(self.temperature)
        
        # Check for bootstrap
        if not self.bootstrapped and self.correlation_length >= XI_CRITICAL:
            self.bootstrapped = True
            print(f"🔥 BOOTSTRAP! at T={self.temperature:.2f}, ξ={self.correlation_length:.2f}")
        
        # Update field based on bootstrap status
        if self.bootstrapped:
            self.update_field_post_bootstrap()
        else:
            self.update_field_pre_bootstrap()
        
        # Track history
        self.temp_history.append(self.temperature)
        self.xi_history.append(self.correlation_length)
        self.time += 1
    
    def get_state(self):
        """Return current state for visualization"""
        return {
            'field': self.field.copy(),
            'temperature': self.temperature,
            'xi': self.correlation_length,
            'bootstrapped': self.bootstrapped,
            'time': self.time
        }

def create_animation():
    """Create animated visualization of bootstrap"""
    universe = UniverseBootstrap()
    
    # Set up the figure
    fig = plt.figure(figsize=(14, 6))
    
    # Main field visualization
    ax_field = plt.subplot(1, 2, 1)
    field_plot = ax_field.imshow(universe.field, cmap='twilight', 
                                   animated=True, vmin=-2, vmax=2)
    ax_field.set_title('Quantum Field', fontsize=14, fontweight='bold')
    ax_field.axis('off')
    plt.colorbar(field_plot, ax=ax_field, fraction=0.046, pad=0.04)
    
    # Status panel
    ax_status = plt.subplot(1, 2, 2)
    ax_status.set_xlim(0, 10)
    ax_status.set_ylim(0, 10)
    ax_status.axis('off')
    
    # Text elements for status
    time_text = ax_status.text(1, 9, '', fontsize=12)
    temp_text = ax_status.text(1, 8, '', fontsize=12)
    xi_text = ax_status.text(1, 7, '', fontsize=12)
    status_text = ax_status.text(1, 5.5, '', fontsize=14, fontweight='bold')
    phase_text = ax_status.text(1, 4, '', fontsize=11, style='italic')
    
    # Progress bars
    temp_bar_bg = patches.Rectangle((1, 2.5), 7, 0.3, 
                                     linewidth=1, edgecolor='black', 
                                     facecolor='lightgray')
    temp_bar = patches.Rectangle((1, 2.5), 0, 0.3,
                                  linewidth=0, facecolor='orangered')
    
    xi_bar_bg = patches.Rectangle((1, 1.5), 7, 0.3,
                                   linewidth=1, edgecolor='black',
                                   facecolor='lightgray')
    xi_bar = patches.Rectangle((1, 1.5), 0, 0.3,
                                linewidth=0, facecolor='dodgerblue')
    
    ax_status.add_patch(temp_bar_bg)
    ax_status.add_patch(temp_bar)
    ax_status.add_patch(xi_bar_bg)
    ax_status.add_patch(xi_bar)
    
    ax_status.text(0.5, 2.65, 'T:', fontsize=10, ha='right')
    ax_status.text(0.5, 1.65, 'ξ:', fontsize=10, ha='right')
    
    def update(frame):
        """Update function for animation"""
        # Run multiple steps per frame for speed
        for _ in range(STEPS_PER_FRAME):
            universe.step()
        
        state = universe.get_state()
        
        # Update field visualization
        field_plot.set_array(state['field'])
        
        # Update status text
        time_text.set_text(f"Time: {state['time']} steps")
        temp_text.set_text(f"Temperature: {state['temperature']:.2f}")
        xi_text.set_text(f"Correlation ξ: {state['xi']:.2f}")
        
        # Update phase status
        if state['bootstrapped']:
            status_text.set_text('⚡ OBSERVATION ACTIVE')
            status_text.set_color('green')
            phase_text.set_text('Reality stabilized.\nStructures persist.\nObservation maintains existence.')
            ax_field.set_title('Quantum Field - POST-BOOTSTRAP', 
                             fontsize=14, fontweight='bold', color='green')
        else:
            if state['xi'] > XI_CRITICAL * 0.7:
                status_text.set_text('⚠️  APPROACHING CRITICAL')
                status_text.set_color('orange')
                phase_text.set_text('Correlation length growing...\nBootstrap imminent.')
            else:
                status_text.set_text('❄️  PRE-BOOTSTRAP')
                status_text.set_color('blue')
                phase_text.set_text('Pure potential.\nRandom fluctuations.\nNo stable structure.')
            ax_field.set_title('Quantum Field - PRE-BOOTSTRAP',
                             fontsize=14, fontweight='bold', color='blue')
        
        # Update progress bars
        temp_fraction = (T_INITIAL - state['temperature']) / (T_INITIAL - T_FINAL)
        temp_bar.set_width(7 * temp_fraction)
        
        xi_fraction = min(state['xi'] / (XI_CRITICAL * 1.5), 1.0)
        xi_bar.set_width(7 * xi_fraction)
        
        if state['xi'] >= XI_CRITICAL:
            xi_bar.set_facecolor('lime')
        elif state['xi'] > XI_CRITICAL * 0.7:
            xi_bar.set_facecolor('yellow')
        else:
            xi_bar.set_facecolor('dodgerblue')
        
        return [field_plot, time_text, temp_text, xi_text, status_text, 
                phase_text, temp_bar, xi_bar]
    
    # Create animation
    anim = FuncAnimation(fig, update, frames=500, interval=50, blit=True)
    
    plt.suptitle('UNIVERSE BOOTSTRAP SIMULATION\nWatching Observation Emerge from Pure Potential',
                 fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    return anim, fig

if __name__ == '__main__':
    print("="*60)
    print("UNIVERSE BOOTSTRAP SIMULATION")
    print("Based on Solvency Field Theory")
    print("="*60)
    print()
    print("Simulating:")
    print("  • Pure potential (random quantum fluctuations)")
    print("  • Temperature cooling")
    print("  • Correlation length increasing")
    print("  • Bootstrap when ξ reaches critical threshold")
    print("  • Observation turning on")
    print("  • Structure stabilization")
    print()
    print("Watch for the green 'OBSERVATION ACTIVE' status!")
    print("="*60)
    print()
    
    try:
        from scipy.ndimage import gaussian_filter
        
        # Create and show animation
        anim, fig = create_animation()
        plt.show()
        
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Install with: pip install numpy matplotlib scipy --break-system-packages")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
