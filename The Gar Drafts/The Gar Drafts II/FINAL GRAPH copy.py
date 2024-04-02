import json
import matplotlib.pyplot as plt
import numpy as np

# Load the JSON data
with open("summary.json", "r") as file:
    data = json.load(file)

# Initialize variables to hold processed data
iterations = list(range(len(data)))  # Assuming each entry in the data is one iteration
force_values_matrix = np.zeros(
    (16, len(data))
)  # 16 indices by the number of iterations

# Process each entry in the JSON data for force values
for entry_index, entry in enumerate(data):
    force_values = entry["force_values"]
    for i, force_value in enumerate(force_values):
        # Set the force value for this index and iteration
        force_values_matrix[i, entry_index] = force_value

# Create a plot for force values
plt.figure(figsize=(15, 10))

# Plot each index's force data as separate rows with spacing
spacing = 10  # Define the spacing between rows to clearly differentiate them
for i in range(16):
    row_y = force_values_matrix[i] + i * spacing  # Offset each row
    plt.plot(
        iterations,
        row_y,
        drawstyle="steps-mid",
        label=f"Index {i}",
    )

# Adjust y-ticks to align with the offset rows and improve readability
plt.yticks([i * spacing for i in range(16)], [f"Index {i}" for i in range(16)])

plt.xlabel("Iteration")
plt.ylabel("Force Value")
plt.title("Force Values Over Iterations")
plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")

plt.tight_layout()
plt.show()
