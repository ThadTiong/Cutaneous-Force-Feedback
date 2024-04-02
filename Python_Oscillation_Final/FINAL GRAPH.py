import json
import matplotlib.pyplot as plt
import numpy as np

# Read the JSON data
with open("summary.json", "r") as file:
    data = json.load(file)

# Initialize variables to hold processed data
iterations = list(range(len(data)))  # Assuming each entry in the data is one iteration
binary_values = np.zeros((16, len(data)))  # 16 indices by the number of iterations
oscillation_counts = np.zeros(16)
force_values_sum = np.zeros(16)  # Sum of force values for averaging
force_values_count = np.zeros(
    16
)  # Count of entries for each index to calculate average

# Process each entry in the JSON data
for entry_index, entry in enumerate(data):
    list_to_use = "new_binary_list" if entry["count"] == 4 else "binary_list"

    for i, value in enumerate(entry[list_to_use]):
        # Set the binary value for this index and iteration
        binary_values[i, entry_index] = value
        # Sum up force values for later averaging
        force_values_sum[i] += entry["force_values"][i]
        force_values_count[i] += 1
        # Count oscillations if not the first entry and the value has changed from the previous
        if entry_index > 0 and value != binary_values[i, entry_index - 1]:
            oscillation_counts[i] += 1

# Calculate average force values
average_force_values = force_values_sum / force_values_count

# Create a combined plot
plt.figure(figsize=(15, 10))

# Plot each index's binary data as separate rows with spacing
spacing = 1.5  # Define the spacing between rows
for i in range(16):
    row_y = binary_values[i] * 0.8 + i * spacing  # Scale and offset each row
    plt.plot(
        iterations,
        row_y,
        drawstyle="steps-mid",
        label=f"Node {i+1}, Avg Force = {average_force_values[i]:.2f}, Oscillations = {oscillation_counts[i]}",
    )

# Adjust y-ticks to align with the scaled and offset rows
plt.yticks([i * spacing for i in range(16)], [f"Node {i+1}" for i in range(16)])

plt.xlabel("Iteration")
plt.ylabel("Index")
plt.title("Binary Values with Average Force Values")
plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")

plt.tight_layout()
plt.show()
