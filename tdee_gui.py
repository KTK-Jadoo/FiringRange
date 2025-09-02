#!/usr/bin/env python3
# tdee_gui.py — Mifflin–St Jeor TDEE calculator with a Tkinter GUI

import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass

# ---------- Conversions ----------
def lbs_to_kg(lbs: float) -> float:
    return lbs * 0.45359237

def kg_to_lbs(kg: float) -> float:
    return kg / 0.45359237

def inches_to_cm(inches: float) -> float:
    return inches * 2.54

def cm_to_inches(cm: float) -> float:
    return cm / 2.54

# ---------- Core formulas ----------
def bmr_mifflin_st_jeor(sex: str, weight_kg: float, height_cm: float, age_years: int) -> float:
    s = sex.lower()
    if s not in ("m", "f"):
        raise ValueError("sex must be 'm' or 'f'")
    base = 10 * weight_kg + 6.25 * height_cm - 5 * age_years
    return base + 5 if s == "m" else base - 161

ACTIVITY_FACTORS = {
    "Sedentary (little/no exercise)": 1.2,
    "Light (1–3 days/wk)": 1.375,
    "Moderate (3–5 days/wk)": 1.55,
    "Very (6–7 days/wk)": 1.725,
    "Athlete (very hard/physical job)": 1.9,
}

# ---------- Model ----------
@dataclass
class Person:
    sex: str          # 'm' or 'f'
    age: int          # years
    weight: float     # numeric
    weight_unit: str  # 'kg' or 'lb'
    height: float     # numeric
    height_unit: str  # 'cm' or 'in'
    activity_label: str  # key from ACTIVITY_FACTORS

    def weight_kg(self) -> float:
        return self.weight if self.weight_unit == "kg" else lbs_to_kg(self.weight)

    def height_cm(self) -> float:
        return self.height if self.height_unit == "cm" else inches_to_cm(self.height)

# ---------- GUI ----------
class TDEEApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mifflin–St Jeor TDEE Calculator")
        self.geometry("520x420")
        self.resizable(False, False)

        main = ttk.Frame(self, padding=16)
        main.pack(fill="both", expand=True)

        # Row 0: Sex, Age
        row = 0
        ttk.Label(main, text="Sex:").grid(row=row, column=0, sticky="w", padx=(0,8), pady=6)
        self.sex_var = tk.StringVar(value="m")
        sex_box = ttk.Combobox(main, textvariable=self.sex_var, values=["m", "f"], state="readonly", width=6)
        sex_box.grid(row=row, column=1, sticky="w")

        ttk.Label(main, text="Age (years):").grid(row=row, column=2, sticky="e", padx=(24,8))
        self.age_var = tk.StringVar()
        age_entry = ttk.Entry(main, textvariable=self.age_var, width=10)
        age_entry.grid(row=row, column=3, sticky="w")

        # Row 1: Weight + unit
        row += 1
        ttk.Label(main, text="Weight:").grid(row=row, column=0, sticky="w", padx=(0,8), pady=6)
        self.weight_var = tk.StringVar()
        ttk.Entry(main, textvariable=self.weight_var, width=10).grid(row=row, column=1, sticky="w")
        self.weight_unit_var = tk.StringVar(value="kg")
        ttk.Combobox(main, textvariable=self.weight_unit_var, values=["kg", "lb"], state="readonly", width=6)\
            .grid(row=row, column=2, sticky="w", padx=(24,0))

        # Row 2: Height + unit
        row += 1
        ttk.Label(main, text="Height:").grid(row=row, column=0, sticky="w", padx=(0,8), pady=6)
        self.height_var = tk.StringVar()
        ttk.Entry(main, textvariable=self.height_var, width=10).grid(row=row, column=1, sticky="w")
        self.height_unit_var = tk.StringVar(value="cm")
        ttk.Combobox(main, textvariable=self.height_unit_var, values=["cm", "in"], state="readonly", width=6)\
            .grid(row=row, column=2, sticky="w", padx=(24,0))

        # Row 3: Activity
        row += 1
        ttk.Label(main, text="Activity level:").grid(row=row, column=0, sticky="w", padx=(0,8), pady=6)
        self.activity_var = tk.StringVar(value=list(ACTIVITY_FACTORS.keys())[1])
        ttk.Combobox(main, textvariable=self.activity_var, values=list(ACTIVITY_FACTORS.keys()), state="readonly", width=30)\
            .grid(row=row, column=1, columnspan=3, sticky="w")

        # Row 4: Buttons
        row += 1
        ttk.Button(main, text="Compute", command=self.compute).grid(row=row, column=0, pady=14, sticky="w")
        ttk.Button(main, text="Clear", command=self.clear).grid(row=row, column=1, pady=14, sticky="w", padx=(8,0))

        # Separator
        row += 1
        ttk.Separator(main, orient="horizontal").grid(row=row, column=0, columnspan=4, sticky="ew", pady=(4,8))

        # Row 6+: Results
        row += 1
        self.bmr_label = ttk.Label(main, text="BMR (kcal/day): —", font=("TkDefaultFont", 10, "bold"))
        self.bmr_label.grid(row=row, column=0, columnspan=4, sticky="w", pady=4)

        row += 1
        self.tdee_label = ttk.Label(main, text="TDEE (kcal/day): —", font=("TkDefaultFont", 11, "bold"))
        self.tdee_label.grid(row=row, column=0, columnspan=4, sticky="w", pady=4)

        row += 1
        self.ref_label = ttk.Label(main, text="Reference: —")
        self.ref_label.grid(row=row, column=0, columnspan=4, sticky="w", pady=(6,0))

    def clear(self):
        self.age_var.set("")
        self.weight_var.set("")
        self.height_var.set("")
        self.sex_var.set("m")
        self.weight_unit_var.set("kg")
        self.height_unit_var.set("cm")
        self.activity_var.set(list(ACTIVITY_FACTORS.keys())[1])
        self.bmr_label.config(text="BMR (kcal/day): —")
        self.tdee_label.config(text="TDEE (kcal/day): —")
        self.ref_label.config(text="Reference: —")

    def compute(self):
        try:
            age = int(self.age_var.get())
            weight = float(self.weight_var.get())
            height = float(self.height_var.get())
            sex = self.sex_var.get()
            w_unit = self.weight_unit_var.get()
            h_unit = self.height_unit_var.get()
            activity = self.activity_var.get()

            # Basic sanity checks (tunable)
            if not (14 <= age <= 90):
                raise ValueError("Age must be between 14 and 90.")
            if w_unit == "kg" and not (30 <= weight <= 300):
                raise ValueError("Weight in kg must be between 30 and 300.")
            if w_unit == "lb" and not (66 <= weight <= 660):
                raise ValueError("Weight in lb must be between 66 and 660.")
            if h_unit == "cm" and not (120 <= height <= 220):
                raise ValueError("Height in cm must be between 120 and 220.")
            if h_unit == "in" and not (47 <= height <= 87):
                raise ValueError("Height in inches must be between 47 and 87.")

            person = Person(
                sex=sex, age=age,
                weight=weight, weight_unit=w_unit,
                height=height, height_unit=h_unit,
                activity_label=activity
            )

            w_kg = person.weight_kg()
            h_cm = person.height_cm()
            bmr = bmr_mifflin_st_jeor(person.sex, w_kg, h_cm, person.age)
            factor = ACTIVITY_FACTORS[activity]
            tdee = bmr * factor

            # Present results
            self.bmr_label.config(text=f"BMR (kcal/day): {bmr:.0f}")
            self.tdee_label.config(text=f"TDEE (kcal/day): {tdee:.0f}")
            self.ref_label.config(
                text=(f"Reference: weight {w_kg:.1f} kg ({kg_to_lbs(w_kg):.1f} lb), "
                      f"height {h_cm:.1f} cm ({cm_to_inches(h_cm):.1f} in), "
                      f"activity factor {factor:.3f}")
            )

        except ValueError as e:
            messagebox.showerror("Invalid input", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Something went wrong:\n{e}")

if __name__ == "__main__":
    # Use ttk theme for nicer defaults
    try:
        app = TDEEApp()
        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")
        app.mainloop()
    except tk.TclError as e:
        print("Tkinter error:", e)
