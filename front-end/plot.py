import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress

# Define the "order" of brain layers:
# 1: Ancient structures (brainstem, basal ganglia, cerebellum)
# 2: Limbic system
# 3: Neocortex
# 4: Prefrontal cortex
layers = np.array([1, 2, 3, 4])

# Approximate emergence times in million years ago (Mya) for each layer
times = np.array([500, 200, 50, 2])  # Mya

# Because the time intervals shrink roughly exponentially, we take the base-10 logarithm.
log_times = np.log10(times)

# Perform a linear regression on (layer, log10(time))
slope, intercept, r_value, p_value, std_err = linregress(layers, log_times)

# Predict the (log10) emergence time for the next layer (Layer 5)
order_next = 5
predicted_log_time = intercept + slope * order_next
predicted_time = 10 ** predicted_log_time

print(f"Predicted emergence time for layer {order_next}: {predicted_time:.2f} million years ago.")

# Create a plot of the observed data and the fitted trend line
plt.figure(figsize=(8, 6))
plt.scatter(layers, times, color='blue', s=80, label='Observed Brain Layers')
plt.scatter(order_next, predicted_time, color='red', s=80, label='Predicted Next Layer')

# Plot the regression (exponential) trend line for orders 1 through 5
order_range = np.linspace(1, 5, 100)
predicted_log_times = intercept + slope * order_range
predicted_times_line = 10 ** predicted_log_times

plt.plot(order_range, predicted_times_line, 'k--', label='Exponential Fit')
plt.yscale('log')  # Use a log scale for time so that the exponential decay appears linear
plt.xlabel('Brain Layer Order\n(1 = Ancient structures; 4 = Prefrontal cortex)')
plt.ylabel('Emergence Time (million years ago)')
plt.title('Evolutionary Emergence of Brain Layers and Predicted Next Layer')
plt.legend()
plt.grid(True, which="both", ls="--", c='gray')
plt.show()
