import json
import matplotlib.pyplot as plt
import numpy as np

# Given list of force values
force_values = [350, 325, 300, 50, 325, 300, 50, 0, 300, 50, 0, 0, 50, 0, 0, 0]

# Read the JSON data
with open('summary.json', 'r') as file:
    data = json.load(file)

# Initialize a dictionary to hold series data for each index, including oscillation counts
series_data = {i: {'iterations': [], 'values': [], 'oscillation_count': 0} for i in range(16)}

# Process each entry in the JSON data
for entry_index, entry in enumerate(data):
    list_to_use = 'new_binary_list' if entry['count'] == 4 else 'binary_list'
    
    for i, value in enumerate(entry[list_to_use]):
        # Add the current value to the series, slightly offset each index for visibility
        series_data[i]['iterations'].append(entry_index + (i * 0.1))  # Offset each index
        series_data[i]['values'].append(value)
        # Count oscillations
        if entry_index > 0 and value != series_data[i]['values'][-2]:
            series_data[i]['oscillation_count'] += 1

# Create a combined plot
plt.figure(figsize=(15, 10))

# Plot each index's data with oscillation count
for i in range(16):
    plt.step(series_data[i]['iterations'], np.array(series_data[i]['values']) + (i * 0.05), where='mid', label=f'Index {i} (Value={force_values[i]}, Osc={series_data[i]["oscillation_count"]})')

plt.xlabel('Iteration')
plt.ylabel('Value (Offset for Visibility)')
plt.title('Combined Binary Values with Oscillation Counts')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

plt.tight_layout()
plt.show()
