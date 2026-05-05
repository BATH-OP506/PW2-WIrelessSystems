# 1. INITIALISATION
IMPORT tools
DEFINE receiver_locations as (x, y, z)  # Z represents floor height
SET room_labels for visual mapping (e.g., '2.26', '2.14')
DEFINE transmit_frequencies (500MHz to 800MHz)
DEFINE RSSI_matrix (Rows: Receivers, Columns: Transmitters)
PRECOMPUTE squared_norms for all receiver positions

# 2. ENHANCED NOISY DISTANCE FUNCTION
FUNCTION calculate_distance_with_noise(measured_rssi, frequency):
    CALCULATE wavelength from frequency (c / f)
    GENERATE random shadowing noise (Gaussian distribution)
    SET environmental constants (Path Loss Exponent gamma = 3.0)
    
    COMPUTE reference_power using Friis equation
    # Solve for distance incorporating random indoor environmental noise
    COMPUTE distance = d0 * 10^((Ref_Power - (measured_rssi + noise)) / (10 * gamma))
    RETURN distance

# 3. MULTI-TRANSMITTER PROCESSING LOOP
FOR each transmitter (1 to 4):
    INITIALISE list for position estimates
    
    # Run multiple trials to simulate real-time signal jitter
    FOR epoch from 1 to 10:
        # A. Signal Processing
        ADD random electronic measurement noise to the RSSI readings
        FOR each receiver:
            CONVERT noisy_rssi to distance using calculate_distance_with_noise()
        
        # B. 3D Trilateration (Linear System Setup)
        CREATE Matrix_A (size 3x3) and Vector_B
        FOR receivers 2, 3, and 4:
            # Map the spatial differences relative to Receiver 1
            Matrix_A row = 2 * (Difference in x, y, and z)
            Vector_B row = (Dist_1^2 - Dist_i^2) + (Norm_i - Norm_1)
            
        # C. Coordinate Estimation
        SOLVE for (x, y, z) using Least Squares (Normal Equation)
        STORE result for this epoch

    # D. Final Statistical Aggregation
    CALCULATE Average_Position (Mean) and Uncertainty (Std Dev) for this Transmitter

# 4. RESULTS & VISUALISATION
FOR each transmitter:
    PRINT the estimated (x, y, z) and the frequency used
    
# 5. MAPPING
PLOT receiver positions as static blue dots with room labels
FOR each transmitter:
    PLOT estimated (x, y) as a colored 'X'
    DRAW error bars representing the Standard Deviation (Uncertainty)
    APPLY labels and grid for corridor map context
SHOW final 2D projection of the 3D localisation