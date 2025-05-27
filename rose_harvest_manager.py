import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

SUMMARY_FOLDER = 'summaries'
TABLES_FOLDER = 'tables'

HARVESTERS_FILE = os.path.join(TABLES_FOLDER, 'harvesters.csv')
HARVEST_DATA_FILE = os.path.join(TABLES_FOLDER, 'rose_harvest.csv')


def ensure_folder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)


def load_or_create_csv(filepath, columns):
    ensure_folder(os.path.dirname(filepath))
    if os.path.exists(filepath):
        return pd.read_csv(filepath)
    else:
        return pd.DataFrame(columns=columns)


def save_csv(df, filepath):
    ensure_folder(os.path.dirname(filepath))
    df.to_csv(filepath, index=False)


def add_harvester():
    name = input("Enter new harvester's name: ").strip().title()
    harvesters_df = load_or_create_csv(HARVESTERS_FILE, ["id", "name"])

    if name in harvesters_df["name"].values:
        print(f"Harvester '{name}' already exists.")
        return

    new_id = int(harvesters_df["id"].max() + 1 if not harvesters_df.empty else 1)
    harvesters_df = harvesters_df._append({"id": new_id, "name": name}, ignore_index=True)
    save_csv(harvesters_df, HARVESTERS_FILE)
    print(f"Harvester '{name}' added with ID {new_id}.")


def add_harvest_data():
    harvesters_df = load_or_create_csv(HARVESTERS_FILE, ["id", "name"])
    harvest_df = load_or_create_csv(HARVEST_DATA_FILE, ["name", "id", "date", "day", "quantity_kg", "sacks"])

    while True:
        name = input("Enter harvester's name (or 'exit' to stop): ").strip().title()
        if name.lower() == "exit":
            break

        matched = harvesters_df[harvesters_df["name"] == name]

        if matched.empty:
            print(f"Harvester '{name}' not found, Add them first.")
            continue

        try:
            quantity = float(input("Enter quantity harvested (kg): "))
            sacks = int(input("Enter number of sacks: "))
        except ValueError:
            print("Invalid input. Please enter numeric values.")
            return

        harvester_id = matched.iloc[0]["id"]

        new_entry = {
            "name": name,
            "id": harvester_id,
            "date": datetime.today().strftime('%d-%m-%y'),
            "day": datetime.today().strftime('%A'),
            "quantity_kg": quantity,
            "sacks": sacks
        }

        harvest_df = harvest_df._append(new_entry, ignore_index=True)
        print(f"Harvest entry added for {name}.\n")

    save_csv(harvest_df, HARVEST_DATA_FILE)
    print("All entries saved.")


def show_harvest():
    if not os.path.exists(HARVEST_DATA_FILE):
        print("No harvest record found.")
        return

    df = pd.read_csv(HARVEST_DATA_FILE)
    print(df)


def daily_summary():
    if not os.path.exists(HARVEST_DATA_FILE):
        print("No harvest data available.")
        return

    df = pd.read_csv(HARVEST_DATA_FILE)

    if df.empty:
        print("Harvest file is empty.")
        return

    available_dates = sorted(df["date"].unique())
    print("\nAvailable dates:")
    print("0. Today")
    for i, date in enumerate(available_dates, 1):
        print(f"{i}. {date}")

    try:
        choice = int(input("\nSelect a date number (or 0 for today's summary): ").strip())
        if choice == 0:
            target_date = datetime.today().strftime('%d-%m-%y')
        elif 1 <= choice <= len(available_dates):
            target_date = available_dates[choice - 1]
        else:
            print("Invalid choice.")
            return
    except ValueError:
        print("Please enter a number.")
        return

    day_df = df[df["date"] == target_date]

    if day_df.empty:
        print(f"No harvest data for {target_date}.")
        return

    total_sacks = day_df["sacks"].sum()
    total_tare_weight = total_sacks * 0.2
    total_net_weight_kg = day_df["quantity_kg"].sum()
    total_gross_weight_kg = total_net_weight_kg + total_tare_weight
    num_harvesters = day_df["name"].nunique()

    breakdown = day_df.groupby(["id", "name"])[["quantity_kg", "sacks"]].sum().sort_index()

    print(f"\n--- Summary for {target_date} ---")
    print(f"Total Sacks Count: {total_sacks}")
    print(f"Total Roses Gross Weight: {total_gross_weight_kg:.1f} kg")
    print(f"Total Tare Weight: {total_tare_weight:.1f}")
    print(f"Total Roses Net Weight: {total_net_weight_kg:.1f} kg")
    print(f"Number of Harvesters: {num_harvesters}")
    print("\nBreakdown by Harvester:")
    print(breakdown)

    ensure_folder(SUMMARY_FOLDER)
    filename = os.path.join(SUMMARY_FOLDER, f"summary_{target_date}.txt".replace("/", "-"))

    with open(filename, "w") as f:
        f.write(f"Rose Harvest Summary for {target_date}\n")
        f.write(f"Total Sacks Count: {total_sacks}\n")
        f.write(f"Total Roses Gross Weight: {total_gross_weight_kg:.1f} kg\n")
        f.write(f"Total Tare Weight: {total_tare_weight:.1f}\n")
        f.write(f"Total Roses Net Weight: {total_net_weight_kg:.1f} kg\n")
        f.write(f"Number of Harvesters: {num_harvesters}\n\n")
        f.write("Breakdown by Harvester:\n")
        f.write(breakdown.to_string())

    print(f"\nSummary saved to: {filename}")


def plot_total_harvest():
    if not os.path.exists(HARVEST_DATA_FILE):
        print("No harvest data available.")
        return

    df = pd.read_csv(HARVEST_DATA_FILE)

    if df.empty:
        print("Harvest file is empty.")
        return

    try:
        df["date"] = pd.to_datetime(df["date"], format="%d-%m-%y")
    except Exception as e:
        print("Error parsing dates:", e)
        return

    daily_totals = df.groupby("date")["quantity_kg"].sum()

    plt.figure(figsize=(10, 5))
    daily_totals.plot(kind="line", marker="o", color="green")
    plt.title("Total Rose Harvest Over Time")
    plt.xlabel("Date")
    plt.ylabel("Quantity (kg)")
    plt.grid(True)
    plt.tight_layout()
    plt.xticks(rotation=45)
    plt.show()


def main():
    while True:
        print("\nRose Harvest Manager")
        print("1. Add new harvester")
        print("2. Add harvest data")
        print("3. Show harvest table")
        print("4. Daily summary")
        print("5. Plot total harvest")
        print("6. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_harvester()
        elif choice == "2":
            add_harvest_data()
        elif choice == "3":
            show_harvest()
        elif choice == "4":
            daily_summary()
        elif choice == "5":
            plot_total_harvest()
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
