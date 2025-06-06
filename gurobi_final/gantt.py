import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from tqdm import tqdm  # Import tqdm for progress bar

# Configuration
MAX_TASKS_PER_MACHINE = 30  # Maximum number of tasks to plot per machine

# Read the CSV file
try:
    df = pd.read_csv('area_dispatcher_results_ETCH.csv')
except FileNotFoundError:
    print("Error: File 'area_dispatcher_results_ETCH.csv' not found. Using provided sample data.")
    exit()

# Ensure columns are in the expected format
expected_columns = ['Machine', 'Processing Start', 'Processing End', 'Loading Start', 'Loading End']
if not all(col in df.columns for col in expected_columns):
    raise ValueError(f"CSV file must contain columns: {expected_columns}")

# Set up the plot
fig, ax = plt.subplots(figsize=(12, len(df['Machine'].unique()) * 0.5 + 1))

# Group tasks by machine and sort machines by numerical order
machines = sorted(df['Machine'].unique(), key=lambda x: int(x.split()[-1]))  # Sort by numerical value
y_positions = {machine: len(machines) - i for i, machine in enumerate(machines)}  # Assign y-position to place Machine 0 at top

# Track max end time for plotted tasks
max_end_time = 0

# Plot tasks for each machine with tqdm progress bar, limiting to MAX_TASKS_PER_MACHINE
for machine in tqdm(machines, desc="Plotting machine tasks"):
    machine_data = df[df['Machine'] == machine].head(MAX_TASKS_PER_MACHINE)  # Limit to configured number of tasks
    y = y_positions[machine]
    for _, row in machine_data.iterrows():
        # Plot processing phase
        ax.broken_barh([(row['Processing Start'], row['Processing End'] - row['Processing Start'])],
                       (y - 0.2, 0.4), facecolors='#4CAF50', edgecolors='#388E3C', linewidth=1)
        # Plot loading phase
        ax.broken_barh([(row['Loading Start'], row['Loading End'] - row['Loading Start'])],
                       (y - 0.2, 0.4), facecolors='#2196F3', edgecolors='#1976D2', linewidth=1)
        # Update max end time
        max_end_time = max(max_end_time, row['Processing End'], row['Loading End'])

# Configure the plot
ax.set_ylim(0.5, len(machines) + 0.5)
ax.set_yticks(list(y_positions.values()))
ax.set_yticklabels(machines)
ax.set_xlim(0, max_end_time + 50)  # Set x-axis to max end time of plotted tasks plus padding
ax.set_xlabel('Time')
ax.set_ylabel('Machine')
ax.grid(True, axis='x', linestyle='--', alpha=0.7)

# Add legend
proc_patch = mpatches.Patch(color='#4CAF50', label='Processing')
load_patch = mpatches.Patch(color='#2196F3', label='Loading')
plt.legend(handles=[proc_patch, load_patch], loc='upper right')

plt.title(f'Gantt Chart for Machine Tasks (First {MAX_TASKS_PER_MACHINE} Tasks per Machine)')
plt.tight_layout()

# Save the plot as an image
plt.savefig('gantt_chart.png', dpi=300, bbox_inches='tight')
print("Gantt chart saved as 'gantt_chart.png'")

# Display the plot (optional, can be removed if only saving is needed)
plt.show()