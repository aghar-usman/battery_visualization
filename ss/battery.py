import pandas as pd
import plotly.express as px
import os

# Define the folder path and metadata file location
folder_path = r"C:\Users\aghar\OneDrive\Documents\Resume"  # Adjust if necessary
metadata_file = "metadata.csv"
metadata_path = os.path.join(folder_path, metadata_file)

# Check if the metadata file exists
if not os.path.exists(metadata_path):
    raise FileNotFoundError(f"Metadata file not found at: {metadata_path}")

# Load the dataset
data = pd.read_csv(metadata_path)

# Print the columns of the dataset
print("Columns in the dataset:", data.columns)

# Ensure necessary columns are present
required_columns = ["Re", "Rct"]
missing_columns = [col for col in required_columns if col not in data.columns]
if missing_columns:
    raise ValueError(f"The dataset is missing the following required columns: {missing_columns}")

# Generate 'Cycle' column if not present
if "Cycle" not in data.columns:
    data["Cycle"] = range(1, len(data) + 1)

# Clean and convert Re and Rct to numeric, coercing invalid entries to NaN
for col in ["Re", "Rct"]:
    data[col] = pd.to_numeric(data[col], errors="coerce")

# Drop rows with NaN values in Re or Rct
data = data.dropna(subset=["Re", "Rct"])

# Remove outliers using the IQR method
def remove_outliers(df, column):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]

data_no_outliers = remove_outliers(data, "Re")
data_no_outliers = remove_outliers(data_no_outliers, "Rct")

# Calculate Battery Impedance
data_no_outliers["Battery_impedance"] = data_no_outliers["Re"] + data_no_outliers["Rct"]

# Smooth data using rolling average
data_no_outliers["Re_smoothed"] = data_no_outliers["Re"].rolling(window=10).mean()
data_no_outliers["Rct_smoothed"] = data_no_outliers["Rct"].rolling(window=10).mean()

# Function to create and display plots
def create_plot(data, y_column, title, y_label, y_range=None):
    """Create and display a line plot for the given column."""
    fig = px.line(
        data,
        x="Cycle",
        y=y_column,
        title=title,
        labels={"Cycle": "Charge/Discharge Cycles", y_column: y_label},
    )
    if y_range:
        fig.update_yaxes(range=y_range)
    fig.update_layout(template="plotly_dark", font=dict(size=16))
    fig.show()

# Plot the smoothed Estimated Electrolyte Resistance (Re)
create_plot(data_no_outliers, "Re_smoothed", "Smoothed Estimated Electrolyte Resistance", "Re (Ohms)")

# Plot the smoothed Charge Transfer Resistance (Rct)
create_plot(data_no_outliers, "Rct_smoothed", "Smoothed Charge Transfer Resistance", "Rct (Ohms)")

# Plot Battery Impedance
create_plot(data_no_outliers, "Battery_impedance", "Battery Impedance vs Cycles", "Impedance (Ohms)")
