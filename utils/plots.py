import matplotlib.pyplot as plt

def plot_metrics(metrics_data_dict, title, output_path):
    plt.figure(figsize=(10, 4))
    for metric_name, data in metrics_data_dict.items():
        if data:
            timestamps, values = zip(*data)
            plt.plot(timestamps, values, label=metric_name)

    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("Usage (%)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
