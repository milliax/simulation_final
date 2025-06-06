import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from tqdm import tqdm
import re

location = "ETCH"
number_of_workers = 4
total_processing_time = 86400  # 24 hours in seconds
dispatching_rule = "fifo"  # FIFO, LIFO, SPTF, LPTF
show_plot = True

filename = f"results/{location}-{number_of_workers}-{total_processing_time}-{dispatching_rule}.csv"
time_limit=6000

df = pd.read_csv(filename)
output_image = f"results/gantt_chart_{filename.split('/')[1].split(".")[0]}.png"

def draw_loading_gantt_chart_from_df():
    fig, ax = plt.subplots(figsize=(12, 8))

    machines = list(df["Machine"].unique())
    machines.reverse()  # To show in a top-down order

    for _, row in df.iterrows():
        y = machines.index(row["Machine"])
        ax.barh(y, row["Processing End"] - row["Processing Start"], left=row["Processing Start"], color='skyblue', edgecolor='black')
        ax.barh(y, row["Loading End"] - row["Loading Start"], left=row["Loading Start"], color='pink', edgecolor='black')

    # Format the plot
    ax.set_yticks(range(len(machines)))
    ax.set_yticklabels(machines)
    ax.set_xlabel("Time")
    ax.set_title("Gantt Chart of Machine Operations")

    # Legend
    processing_patch = mpatches.Patch(color='skyblue', label='Processing')
    loading_patch = mpatches.Patch(color='pink', label='Loading')
    ax.legend(handles=[processing_patch, loading_patch])

    plt.tight_layout()
    plt.grid(True, axis='x', linestyle='--', alpha=0.5)

    load_patch = mpatches.Patch(color='#2196F3', label='Loading')
    ax.legend(handles=[load_patch], loc='upper right')
    ax.set_title(f'Gantt Chart (Loading Only, First {time_limit} Seconds)')

    plt.tight_layout()
    plt.savefig(output_image, dpi=300)

    print(f"Gantt chart saved to '{output_image}'")

    if show_plot:
        plt.show()

draw_loading_gantt_chart_from_df()