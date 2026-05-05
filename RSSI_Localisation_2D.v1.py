# 1. INITIALISATION
IMPORT libraries
DEFINE beacon_positions as a matrix of (x, y) coordinates
SET number_of_test_runs (N) to 10
CALCULATE k_values (x^2 + y^2) for each beacon position

# 2. DISTANCE MODELLING FUNCTION
FUNCTION calculate_distance_from_rssi(measured_signal_strength):
    SET constants (Transmit Power, Antenna Gains, Wavelength, Path Loss Exponent)
    CALCULATE Expected Power at 1 meter using Friis Equation
    
    # Use the Log-Distance Path Loss model
    COMPUTE distance = reference_dist * 10^((Expected_Power - measured_signal) / (10 * Exponent))
    RETURN distance

# 3. MAIN LOCALISATION LOOP
CREATE empty_list to store predicted_positions

FOR each epoch (run) from 1 to N:
    # A. Convert signals to physical meters
    FOR each beacon:
        GET current RSSI measurement
        CONVERT RSSI to distance using calculate_distance_from_rssi()
        STORE in distance_array

    # B. Linearise the geometry (Trilateration)
    # We use the first beacon as the origin reference (0,0) point
    CREATE Matrix_A and Vector_B
    FOR each beacon from index 1 to 3:
        Matrix_A row = 2 * (difference between current beacon and first beacon)
        Vector_B row = (distance_to_first^2 - distance_to_current^2) + (k_current - k_first)

    # C. Solve for (x, y) coordinates
    # Use the Least Squares formula: (A.T * A)^-1 * A.T * B
    estimated_position = SOLVE linear system (Matrix_A, Vector_B)
    SAVE estimated_position to list

# 4. DATA ANALYSIS & OUTPUT
CALCULATE average_x and average_y from predicted_positions
CALCULATE standard_deviation to determine system "jitter" or error

PRINT "The transmitter is likely located at: (average_x, average_y)"
PRINT "Confidence/Spread of data: (standard_deviation)"
