import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from tqdm import tqdm
import re

location = "ETCH"
number_of_workers = 4
total_processing_time = 86400  # 24 hours in seconds

filename = f"results/{location}-{number_of_workers}-{total_processing_time}.csv"
time_limit=6000

df = pd.read_csv(filename)
output_image = f"results/gantt_chart_{filename.split('/')[1].split(".")[0]}.png"

def draw_loading_gantt_chart_from_df(
    df: pd.DataFrame,
    output_image: str = "gantt_chart_loading_only.png",
    max_tasks_per_machine: int = 50,
    show_plot: bool = True
):
    """
    Draws a Gantt chart for loading times only using a DataFrame.

    Args:
        df (pd.DataFrame): DataFrame with columns: 'Machine', 'Processing Start', 'Processing End', 'Loading Start', 'Loading End'.
        output_image (str): Path to save the output image.
        time_limit (int): Only tasks with Loading Start <= time_limit will be shown.
        max_tasks_per_machine (int): Max number of tasks to display per machine.
        show_plot (bool): Whether to display the plot with plt.show().
    """
    def extract_machine_number(name):
        match = re.search(r'\d+', str(name))
        return int(match.group()) if match else float('inf')

    required_cols = ['Machine', 'Processing Start',
                     'Processing End', 'Loading Start', 'Loading End']
    if not all(col in df.columns for col in required_cols):
        raise ValueError(f"DataFrame must include columns: {required_cols}")

    # Filter tasks
    df = df[df['Loading Start'] <= time_limit]

    # Sort machines
    machines = sorted(df['Machine'].unique(), key=extract_machine_number)
    y_positions = {machine: len(machines) - i for i,
                   machine in enumerate(machines)}

    # Plot
    fig, ax = plt.subplots(figsize=(16, len(machines) * 0.4 + 1))
    max_time = 0

    for machine in tqdm(machines, desc="Plotting loading tasks"):
        y = y_positions[machine]
        data = df[df['Machine'] == machine].head(max_tasks_per_machine)

        for _, row in data.iterrows():
            load_start = row['Loading Start']
            load_end = row['Loading End']

            ax.broken_barh([(load_start, load_end - load_start)],
                           (y - 0.3, 0.6),
                           facecolors='#2196F3', edgecolors='#1976D2')

            max_time = max(max_time, load_end)

    ax.set_ylim(0.5, len(machines) + 0.5)
    ax.set_yticks(list(y_positions.values()))
    ax.set_yticklabels(machines)
    ax.set_xlim(0, min(max_time + 50, time_limit))
    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Machine")
    ax.grid(True, axis='x', linestyle='--', alpha=0.6)

    load_patch = mpatches.Patch(color='#2196F3', label='Loading')
    ax.legend(handles=[load_patch], loc='upper right')
    ax.set_title(f'Gantt Chart (Loading Only, First {time_limit} Seconds)')

    plt.tight_layout()
    plt.savefig(output_image, dpi=300)
    print(f"Gantt chart saved to '{output_image}'")

    if show_plot:
        plt.show()

draw_loading_gantt_chart_from_df(
    df,
    max_tasks_per_machine=30,
    show_plot=True
)