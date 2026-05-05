import numpy as np
import matplotlib.pyplot as plt

# --- 1. CONFIGURATION & DATA ---

# Beacon positions in meters [x, y]
beacon_matrix = np.array([[2.81, 0.74],
                          [3.93, 10.97],
                          [8.77, 0.84],
                          [8.77, 10.04]])

# Number of measurement cycles (epochs) to process
N = 10

# Extract cartesian positions for k-value pre-calculation
# k represents the squared norm of the beacon coordinates: k = x^2 + y^2
x = beacon_matrix[:, 0]
y = beacon_matrix[:, 1]
k = x**2 + y**2

# --- 2. SIGNAL MODELLING ---

def rssi_to_distance(Pr_dBm, Pt_dBm, Gt, Gr, d0, gamma, Xg_dB, wavelength):
    """
    Converts RSSI (dBm) to a physical distance (m) using the Log-Distance Path Loss model.
    
    Args:
        Pr_dBm (float): Received Signal Strength Indicator measured by receiver.
        Pt_dBm (float): Transmit power of the beacon (in dBm).
        Gt (float): Linear gain of the transmitter antenna.
        Gr (float): Linear gain of the receiver antenna.
        d0 (float): Reference distance (typically 1.0m) for the path loss model.
        gamma (float): Path-loss exponent (characterizes the environment).
        Xg_dB (float): Gaussian noise/shadowing term (in dB).
        wavelength (float): Wavelength of the signal (in meters).
        
    Returns:
        float: Calculated distance (d) in meters.
    """
    # Convert Pt from dBm to Watts: $P_w = 10^{(P_{dBm}/10)} / 1000$
    Pt_W = 10**(Pt_dBm / 10) / 1000  

    # Calculate theoretical power at reference distance d0 using Friis Transmission Equation
    # Resulting unit is dBm.
    Pr_calc_dBm = 10 * np.log10(Pt_W * Gt * Gr * (wavelength / (4 * np.pi * d0))**2 / 1e-3)

    # Solve for distance (d) using the Log-Distance Path Loss formula:
    # $d = d_0 \cdot 10^{\frac{Pr_{calc} - Pr_{meas} + X_g}{10\gamma}}$
    d = d0 * 10**((Pr_calc_dBm - Pr_dBm + Xg_dB) / (10 * gamma))
    return d

# RSSI measurements (dBm) from the 4 beacons
Pr_dBm = np.array([-50, -80, -69, -35])

# rhat will store the estimated (x, y) coordinates for each of the N epochs
rhat = np.zeros((N, 2))

# --- 3. LOCALISATION LOOP ---

for p in range(N):
    # Initialize distance array for the current epoch
    d = np.zeros(len(beacon_matrix))

    # Calculate distance to each beacon based on RSSI
    for i in range(len(Pr_dBm)):
        d[i] = rssi_to_distance(
            Pr_dBm[i],     # RSSI measurement
            Pt_dBm=-60,    # Transmit power (dBm)
            Gt=2, Gr=2,    # Antenna gains
            d0=8,          # Reference distance (m)
            gamma=2.2,     # Path-loss exponent
            Xg_dB=0.2,     # Shadowing noise (dB)
            wavelength=0.6 # Signal wavelength (m)
        )  

    # Set up the linearized system for trilateration ($A \cdot x = b$)
    # We use (n-1) equations by comparing all beacons to the first beacon (index 0)
    A = np.zeros((len(d) - 1, 2))
    b = np.zeros(len(d) - 1)
    
    for i in range(1, len(d)):
        # Construct Matrix A: $2 \cdot (x_i - x_0, y_i - y_0)$
        A[i - 1, :] = 2 * (beacon_matrix[i, :] - beacon_matrix[0, :])
        
        # Construct Vector b: $(d_0^2 - d_i^2) + (k_i - k_0)$
        b[i - 1] = d[0]**2 - d[i]**2 + k[i] - k[0]

    # Solve for the position estimate using the Ordinary Least Squares (OLS) Normal Equation:
    # $\hat{r} = (A^T A)^{-1} A^T b$
    rhat[p, :] = np.linalg.inv(A.T @ A) @ A.T @ b

# --- 4. OUTPUTS ---

# Compute the average position across all epochs and the standard deviation (spread)
r_mean = np.mean(rhat, axis=0)  # Central estimate
rstd = np.std(rhat, axis=0)     # Measurement jitter/uncertainty

print("Estimated position (x, y) in meters:", r_mean)
print("Position standard deviation (x, y):", rstd)
