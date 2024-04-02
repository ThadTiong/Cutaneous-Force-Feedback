import json
import matplotlib.pyplot as plt

# Given list of force values
force_values = [350, 325, 300, 50, 325, 300, 50, 0, 300, 50, 0, 0, 50, 0, 0, 0]

# Read the JSON data
with open("summary.json", "r") as file:
    data = json.load(file)

# Initialize a dictionary to hold series data for each index, including oscillation counts
series_data = {
    i: {"iterations": [], "values": [], "oscillation_count": 0} for i in range(16)
}

# Process each entry in the JSON data
for entry_index, entry in enumerate(data):
    list_to_use = "new_binary_list" if entry["count"] == 4 else "binary_list"

    for i, value in enumerate(entry[list_to_use]):
        # Add the current value to the series
        series_data[i]["iterations"].append(entry_index)
        series_data[i]["values"].append(value)
        # Count oscillations
        if entry_index > 0 and value != series_data[i]["values"][-2]:
            series_data[i]["oscillation_count"] += 1


# Function to create plots for a given range of indices
def create_plots(start_index, end_index):
    fig, axs = plt.subplots(
        2, 2, figsize=(15, 10)
    )  # Adjust the subplot layout as needed
    fig.tight_layout(pad=4.0)
    for n, ax in enumerate(axs.flatten(), start=start_index):
        if n < end_index:
            ax.step(series_data[n]["iterations"], series_data[n]["values"], where="mid")
            # Include force value and oscillation count in the title
            title = f'Index {n} - Value = {force_values[n]}, Oscillation Count = {series_data[n]["oscillation_count"]}'
            ax.set_title(title)
            ax.set_ylim(-0.1, 1.1)
            ax.set_yticks([0, 1])
            ax.set_xlabel("Iteration")
            ax.set_ylabel("Value")
    plt.show()


# Create plots in batches of 4
for i in range(0, 16, 4):
    create_plots(i, i + 4)
