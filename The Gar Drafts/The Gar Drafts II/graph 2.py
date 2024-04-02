import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# Read the JSON data
with open("summary.json", "r") as file:
    data = json.load(file)

# Initialize a dictionary to hold time series data for each index
time_series_data = {i: {"times": [], "values": []} for i in range(16)}

# Process each entry in the JSON data
for entry in data:
    current_time = datetime.utcfromtimestamp(entry["current_time"])
    list_to_use = "new_binary_list" if entry["count"] == 4 else "binary_list"
    vibration_times = (
        "new_vibration_start_times" if entry["count"] == 4 else "vibration_start_times"
    )

    for i, value in enumerate(entry[list_to_use]):
        time_series_data[i]["times"].append(current_time)
        time_series_data[i]["values"].append(value)


# Function to create plots for a given range of indices
def create_plots(start_index, end_index):
    fig, axs = plt.subplots(
        2, 2, figsize=(15, 10)
    )  # Adjust the subplot layout as needed
    fig.tight_layout(pad=4.0)
    for n, ax in enumerate(axs.flatten(), start=start_index):
        if n < end_index:
            ax.step(
                time_series_data[n]["times"], time_series_data[n]["values"], where="mid"
            )
            ax.set_title(f"Index {n}")
            ax.set_ylim(-0.1, 1.1)
            ax.set_yticks([0, 1])
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
            ax.xaxis.set_major_locator(mdates.DayLocator())
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    plt.show()


# Create plots in batches of 4
for i in range(0, 16, 4):
    create_plots(i, i + 4)
