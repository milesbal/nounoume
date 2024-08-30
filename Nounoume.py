import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from datetime import datetime, timedelta
from tkcalendar import DateEntry

def calculate_monthly_data(base_rate, num_days_per_week, daily_hours, meal_compensation, transport_cost, start_date, end_date):
    # Convert datetime.date to pandas.Timestamp for consistency
    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)

    # Check if the dates are in the same month and do not exceed 1 month duration
    if start_date.month != end_date.month or end_date.year != start_date.year:
        messagebox.showerror("Error", "Dates must be within the same month and year.")
        return pd.DataFrame()

    # Initialize variables
    total_working_days = 0
    weekdays_per_week = {}

    # Calculate number of working days (Monday to Friday) per week within the date range
    current_day = start_date
    while current_day <= end_date:
        week_number = current_day.isocalendar()[1]
        if week_number not in weekdays_per_week:
            weekdays_per_week[week_number] = 0
        if current_day.weekday() < 5:  # Monday to Friday
            weekdays_per_week[week_number] += 1
            total_working_days += 1
        current_day += timedelta(days=1)

    # Calculate total hours and costs for each week
    total_salary = 0
    total_meal_compensation = 0
    total_transport_cost = transport_cost  # Applied only once per month

    for week, count in weekdays_per_week.items():
        hours_per_week = count * daily_hours  # Adjust hours based on actual weekdays worked
        effective_hour_count = min(hours_per_week, 40)
        hours_40_to_48 = max(0, min(hours_per_week - 40, 8))
        hours_over_48 = max(0, hours_per_week - 48)

        salary_effective_hours = round(effective_hour_count * base_rate, 2)
        salary_hours_40_to_48 = round(hours_40_to_48 * base_rate * 1.25, 2)
        salary_hours_over_48 = round(hours_over_48 * base_rate * 1.5, 2)
        weekly_salary = round(salary_effective_hours + salary_hours_40_to_48 + salary_hours_over_48, 2)

        weekly_meal_compensation = round(count * meal_compensation, 2)

        # Sum up weekly totals for the entire date range
        total_salary += weekly_salary
        total_meal_compensation += weekly_meal_compensation

    # Calculate the total monthly cost
    total_monthly_cost = round(total_salary + total_meal_compensation + total_transport_cost, 2)

    # Prepare data for display and export
    month_str = start_date.strftime('%B %Y')
    data = [[month_str, total_monthly_cost, total_transport_cost, total_meal_compensation, total_salary]]

    return pd.DataFrame(data, columns=[
        "Month", "Total Monthly Cost (€)", "Transport Cost (€)", "Meal Compensation (€)", "Total Salary (€)"
    ])

def calculate_and_display():
    global df

    try:
        # Read inputs
        base_salary = float(base_salary_entry.get().replace(',', '.'))
        if base_salary < 9.56:
            messagebox.showerror("Error", "Base salary cannot be lower than €9.56.")
            return

        num_days_per_week = int(num_days_entry.get())
        daily_hours = float(daily_hours_entry.get().replace(',', '.'))
        meal_compensation = float(meal_compensation_entry.get().replace(',', '.'))
        transport_cost = float(transport_cost_entry.get().replace(',', '.'))

        start_date = start_date_entry.get_date()
        end_date = end_date_entry.get_date()

        if end_date < start_date:
            messagebox.showerror("Error", "End date must be after start date.")
            return

        df = calculate_monthly_data(base_salary, num_days_per_week, daily_hours, meal_compensation, transport_cost, start_date, end_date)

        # Clear previous results
        for widget in result_frame.winfo_children():
            widget.destroy()

        if df.empty:
            summary_text.set("No valid data to display.")
            return

        # Display results
        columns = df.columns
        for i, value in enumerate(columns):
            tk.Label(result_frame, text=value).grid(row=0, column=i, padx=5, pady=5, sticky="w")

        for i, row in df.iterrows():
            for j, value in enumerate(row):
                tk.Label(result_frame, text=value).grid(row=1, column=j, padx=5, pady=5)

        export_button.config(state=tk.NORMAL)
        summary_text.set(f"Results for {start_date.strftime('%B %Y')} are displayed below.")

    except ValueError:
        messagebox.showerror("Input Error", "Please check your inputs and ensure they are valid numbers.")

def export_to_csv():
    try:
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if filename:
            df.to_csv(filename, index=False)
            messagebox.showinfo("Export", f"Data exported to {filename}")
    except Exception as e:
        messagebox.showerror("Export Error", f"Error exporting to CSV: {e}")

# Create the main window
root = tk.Tk()
root.title("Monthly Salary Calculator")

# Define and place widgets
tk.Label(root, text="Base Salary (€):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
base_salary_entry = tk.Entry(root)
base_salary_entry.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Number of Days Per Week:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
num_days_entry = tk.Entry(root)
num_days_entry.grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="Daily Hours:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
daily_hours_entry = tk.Entry(root)
daily_hours_entry.grid(row=2, column=1, padx=10, pady=5)

tk.Label(root, text="Meal Compensation (€):").grid(row=3, column=0, padx=10, pady=5, sticky="e")
meal_compensation_entry = tk.Entry(root)
meal_compensation_entry.grid(row=3, column=1, padx=10, pady=5)

tk.Label(root, text="Transport Cost (€):").grid(row=4, column=0, padx=10, pady=5, sticky="e")
transport_cost_entry = tk.Entry(root)
transport_cost_entry.grid(row=4, column=1, padx=10, pady=5)

tk.Label(root, text="Start Date (YYYY-MM-DD):").grid(row=5, column=0, padx=10, pady=5, sticky="e")
start_date_entry = DateEntry(root, date_pattern='yyyy-mm-dd')
start_date_entry.grid(row=5, column=1, padx=10, pady=5)

tk.Label(root, text="End Date (YYYY-MM-DD):").grid(row=6, column=0, padx=10, pady=5, sticky="e")
end_date_entry = DateEntry(root, date_pattern='yyyy-mm-dd')
end_date_entry.grid(row=6, column=1, padx=10, pady=5)

calculate_button = tk.Button(root, text="Calculate", command=calculate_and_display)
calculate_button.grid(row=7, column=0, columnspan=2, pady=10)

export_button = tk.Button(root, text="Export to CSV", command=export_to_csv, state=tk.DISABLED)
export_button.grid(row=8, column=0, columnspan=2, pady=10)

result_frame = tk.Frame(root)
result_frame.grid(row=9, column=0, columnspan=2, padx=10, pady=10)

summary_text = tk.StringVar()
summary_label = tk.Label(root, textvariable=summary_text)
summary_label.grid(row=7, column=2, columnspan=2, padx=10, pady=5)

root.mainloop()