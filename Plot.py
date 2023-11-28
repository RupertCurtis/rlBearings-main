import pandas as pd
import matplotlib.pyplot as plt
import time

# Replace 'your_data.csv' with the path to your CSV file
csv_file = 'liveLogs/log.csv'

def read_and_plot_csv():
    try:
        # Read the CSV file into a DataFrame
        df = pd.read_csv(csv_file)

        # Assuming your CSV file has columns 'x' and 'y1' and 'y2', you can change these to match your file
        x = df['episode']
        y1 = df['length']
        y2 = df['reward']

        # Clear the previous plot (if any)
        plt.clf()

        # Create a new plot with two subplots
        plt.subplot(2, 1, 1)
        plt.plot(x, y1, label='Episode length', color='blue')
        plt.xlabel('X-axis')
        plt.ylabel('Y1-axis')
        plt.legend()

        plt.subplot(2, 1, 2)
        plt.plot(x, y2, label='Reward', color='red')
        plt.xlabel('X-axis')
        plt.ylabel('Y2-axis')
        plt.legend()

        # Adjust layout to prevent overlap
        plt.tight_layout()

        # Display the plot
        plt.pause(0.1)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    while True:
        read_and_plot_csv()
