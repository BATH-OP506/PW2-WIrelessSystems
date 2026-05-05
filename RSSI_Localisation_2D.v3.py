import numpy as np
import matplotlib.pyplot as plt

# Beacon positions
beacon_matrix = np.array([[2.81, 0.74],
                          [3.93, 10.97],
                          [8.77, 0.84],
                          [8.77, 10.04]])

# Number of epochs
N = 10

# Extract cartesian positions
x = beacon_matrix[:, 0]
y = beacon_matrix[:, 1]
k = x**2 + y**2

# RSSI to distance function
def rssi_to_distance(Pr_dBm, Pt_dBm, Gt, Gr, d0, gamma, Xg_dB, wavelength):
    """
    Convert RSSI (dBm) to distance (meters)
    Pt_dBm: transmit power in dBm
    """
    # Convert Pt from dBm to Watts
    Pt_W = 10**(Pt_dBm / 10) / 1000  # dBm -> Watts

    # Friis formula in dBm
    Pr_calc_dBm = 10 * np.log10(Pt_W * Gt * Gr * (wavelength / (4*np.pi*d0))**2 / 1e-3)

    # Calculate distance
    d = d0 * 10**((Pr_calc_dBm - Pr_dBm + Xg_dB) / (10*gamma))
    return d

# RSSI measurements (dBm)
Pr_dBm = np.array([-50, -80, -69, -35])

# rhat will store position estimates for the N epochs
rhat = np.zeros((N, 2))

# Trilateration loop
for p in range(N):
    d = np.zeros(len(beacon_matrix))

    for i in range(len(Pr_dBm)):
        d[i] = rssi_to_distance(
            Pr_dBm[i],     # RSSI measurement for beacon i
            Pt_dBm=-60,    # transmit power in dBm
            Gt=2, Gr=2,    # antenna gains
            d0=8,          # reference distance in meters
            gamma=2.2,     # path-loss exponent
            Xg_dB=0.2,     # shadowing (dB)
            wavelength=0.6 # wavelength in meters
        )  

    # Set up linear system for trilateration
    A = np.zeros((len(d) - 1, 2))
    b = np.zeros(len(d) - 1)
    for i in range(1, len(d)):
        A[i - 1, :] = 2 * (beacon_matrix[i, :] - beacon_matrix[0, :])
        b[i - 1] = d[0]**2 - d[i]**2 + k[i] - k[0]

    # Solve for position estimate
    rhat[p, :] = np.linalg.inv(A.T @ A) @ A.T @ b

# Compute average position and standard deviation
r_mean = np.mean(rhat, axis=0)  # average position
rstd = np.std(rhat, axis=0)     # spread

print("Estimated position (x, y):", r_mean)
print("Position standard deviation (x, y):", rstd)
          
    
    
