import os
import subprocess
import matplotlib.pyplot as plt
import numpy as np
from plot_utils import (
    plot_bandwidth_waste, plot_smoothed_bandwidth_waste, plot_data_transfers,
    plot_used_vs_wasted_bandwidth, plot_bandwidth_waste_distribution,
    plot_failures_vs_bandwidth_waste, plot_used_vs_wasted_bandwidth_dual_axis
)


CONFIG_FILES = ['./configs/p2p.cfg', './configs/client_server.cfg', './configs/p2pHighDownload.cfg', './configs/p2pUpDownE.cfg']

# The list of plot files that "storage.py" typically generates
PLOT_FILES = [
    "bandwidth_waste_over_time.png",
    "smoothed_bandwidth_waste.png",
    "data_transfers_over_time.png",
    "used_vs_wasted_bandwidth_stacked.png",
    "bandwidth_waste_distribution.png",
    "used_vs_wasted_bandwidth_dual_axis.png",
    "failures_vs_bandwidth_waste.png",
    "failures_vs_bandwidth_waste_with_availability.png"
]


############################
# Helpers
############################
def run_simulation(config_file, parallel):
    """Run the simulation for a given config file in parallel or sequential mode."""
    mode_str = "parallel" if parallel else "sequential"
    output_dir = f'plots/{config_file[:-4]}_{mode_str}'
    os.makedirs(output_dir, exist_ok=True)
    
    cmd = [
        'python3', 'storage.py', config_file,
        '--max-t', '100 years'
    ]
    if parallel:
        cmd.append('--parallel')

    result = subprocess.run(cmd, capture_output=True, text=True)
    # Save console output and errors
    with open(f'{output_dir}/log.txt', 'w') as f:
        f.write(result.stdout)
        f.write(result.stderr)


def side_by_side_image(seq_path, par_path, out_path, title="Comparison"):
    """Utility function to display two images side by side and save the result."""
    if not (os.path.exists(seq_path) and os.path.exists(par_path)):
        # If either file doesn't exist, skip.
        return
    
    seq_img = plt.imread(seq_path)
    par_img = plt.imread(par_path)
    
    plt.figure(figsize=(12,6))

    # Left subplot
    plt.subplot(1,2,1)
    plt.imshow(seq_img)
    plt.title("Sequential")
    plt.axis("off")

    # Right subplot
    plt.subplot(1,2,2)
    plt.imshow(par_img)
    plt.title("Parallel")
    plt.axis("off")

    plt.suptitle(title)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def compare_config_plots(config_file):
    """Generate side-by-side comparisons for a single config file."""
    base_name = config_file[:-4]
    seq_dir = f"plots/{base_name}_sequential"
    par_dir = f"plots/{base_name}_parallel"

    compare_output_dir = f"plots/{base_name}_comparison"
    os.makedirs(compare_output_dir, exist_ok=True)

    for plot_file in PLOT_FILES:
        seq_path = os.path.join(seq_dir, plot_file)
        par_path = os.path.join(par_dir, plot_file)
        out_path = os.path.join(compare_output_dir, f"comparison_{plot_file}")
        # We pass a relevant title
        title = f"{base_name}: {plot_file}"
        side_by_side_image(seq_path, par_path, out_path, title=title)


def create_summary_markdown():
    """Generate a markdown summary report that references the comparison images."""
    summary_path = "plots/comparison_report.md"
    with open(summary_path, "w") as f:
        f.write("# Comparison Report for Parallel vs. Sequential\n\n")
        f.write("This report shows side-by-side comparisons of the generated plots for each configuration.\n\n")
        for config_file in CONFIG_FILES:
            base_name = config_file[:-4]
            compare_output_dir = f"plots/{base_name}_comparison"
            if not os.path.isdir(compare_output_dir):
                continue
            
            f.write(f"## {base_name}\n\n")
            for plot_file in PLOT_FILES:
                out_file = f"comparison_{plot_file}"
                out_path = os.path.join(compare_output_dir, out_file)
                if os.path.exists(out_path):
                    f.write(f"### {plot_file}\n")
                    f.write(f"![Comparison]({os.path.relpath(out_path)})\n\n")
            f.write("\n\n")

    print(f"Summary report saved to {summary_path}")


def compare_plots():
    """Compare the generated plots from sequential vs. parallel runs for each config."""
    for config_file in CONFIG_FILES:
        compare_config_plots(config_file)
    create_summary_markdown()


def run_all_simulations():
    for config_file in CONFIG_FILES:
        # 1) Run sequential
        run_simulation(config_file, parallel=False)
        # 2) Run parallel
        run_simulation(config_file, parallel=True)
    # Now compare
    compare_plots()


def main():
    run_all_simulations()
    print("All simulations completed and comparisons generated.")


if __name__ == '__main__':
    main()
