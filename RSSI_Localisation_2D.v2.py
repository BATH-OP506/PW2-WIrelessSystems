import numpy as np # Essential for the matrix math

# --- 1. SETTINGS & DATA ---
# Beacon (x, y) coordinates
beacons = np.array([[2.8, 0.7], [3.9, 10.9], [8.7, 0.8], [8.7, 10.0]])
N_trials = 10
actual_rssi_readings = [-50, -80, -69, -35]

# Pre-calculate k = x^2 + y^2 for the trilateration math
k_values = [pos[0]**2 + pos[1]**2 for pos in beacons]

# --- 2. THE DISTANCE ENGINE ---
def get_meters_from_rssi(rssi_value):
    # Setup our environment constants
    tx_power = -60 
    path_loss_exp = 2.2
    wavelength = 0.6
    
    # Calculate what the signal 'should' be at 1 meter (Friis Math)
    ref_power = tx_power + math_logic(wavelength, antenna_gains)
    
    # Use Log-Distance formula to find distance 'd'
    # d = d0 * 10^((Ref - Measured) / (10 * Exp))
    dist = 8 * 10**((ref_power - rssi_value) / (22))
    return dist

# --- 3. THE LOCALISATION LOOP ---
results_list = []

for run in range(N_trials):
    # A. Convert current RSSI to Distances
    distances = []
    for signal in actual_rssi_readings:
        d = get_meters_from_rssi(signal)
        distances.append(d)
        
    # B. Build the Linear System (Matrix A and Vector B)
    # We compare beacons 2, 3, and 4 against beacon 1
    A_rows = []
    B_rows = []
    
    for i in range(1, 4):
        # A row is 2 * the difference in coordinates
        A_rows.append(2 * (beacons[i] - beacons[0]))
        
        # B row is the distance math: (d1^2 - di^2) + (ki - k1)
        b_val = (distances[0]**2 - distances[i]**2) + (k_values[i] - k_values[0])
        B_rows.append(b_val)

    # C. Solve for (x, y) using Least Squares
    # This is the matrix math: (A_transpose * A)^-1 * A_transpose * B
    A = np.array(A_rows)
    B = np.array(B_rows)
    
    current_estimate = np.solve_least_squares(A, B)
    results_list.append(current_estimate)

# --- 4. WRAP UP ---
final_x_y = np.mean(results_list, axis=0)
uncertainty = np.std(results_list, axis=0)

print(f"Predicted Position: {final_x_y}")
print(f"Jitter/Error: {uncertainty}")

