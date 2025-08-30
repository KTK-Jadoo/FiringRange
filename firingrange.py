""" Mifflin-St Jeor TDEE calculator with robust I/O and unit handling """
#!/usr/bin/env python3

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
    """
    sex: 'm' or 'f'
    Returns Basal Metabolic Rate (kcal/day).
    """
    s = sex.lower()
    if s not in ("m", "f"):
        raise ValueError("sex must be 'm' or 'f'")
    base = 10 * weight_kg + 6.25 * height_cm - 5 * age_years
    return base + 5 if s == "m" else base - 161

# Standard ACSM-style multipliers
ACTIVITY_FACTORS = {
    "sedentary": 1.2,              # little or no exercise
    "light": 1.375,                # 1–3 days/wk
    "moderate": 1.55,              # 3–5 days/wk
    "very": 1.725,                 # 6–7 days/wk
    "athlete": 1.9,                # very hard exercise/physical job
}

def tdee_from_bmr(bmr: float, activity_key: str) -> float:
    key = activity_key.lower()
    if key not in ACTIVITY_FACTORS:
        raise ValueError(f"activity must be one of: {', '.join(ACTIVITY_FACTORS)}")
    return bmr * ACTIVITY_FACTORS[key]

# ---------- Data model (optional but clean) ----------
@dataclass
class Person:
    sex: str          # 'm' or 'f'
    age: int          # years
    weight: float     # numeric
    weight_unit: str  # 'kg' or 'lb'
    height: float     # numeric
    height_unit: str  # 'cm' or 'in'
    activity: str     # one of ACTIVITY_FACTORS keys

    def weight_kg(self) -> float:
        return self.weight if self.weight_unit.lower() == "kg" else lbs_to_kg(self.weight)

    def height_cm(self) -> float:
        return self.height if self.height_unit.lower() == "cm" else inches_to_cm(self.height)

# ---------- CLI helpers ----------
def ask_float(prompt: str) -> float:
    while True:
        try:
            return float(input(prompt).strip())
        except ValueError:
            print("Please enter a number.")

def ask_int(prompt: str) -> int:
    while True:
        try:
            return int(input(prompt).strip())
        except ValueError:
            print("Please enter an integer.")

def ask_choice(prompt: str, choices):
    choices_lower = [c.lower() for c in choices]
    while True:
        val = input(prompt).strip().lower()
        if val in choices_lower:
            return val
        print(f"Please choose one of: {', '.join(choices)}")

def main():
    print("=== Mifflin–St Jeor Daily Energy Expenditure Tool ===")
    sex = ask_choice("Sex (m/f): ", ["m", "f"])
    age = ask_int("Age (years): ")

    # Weight
    w_unit = ask_choice("Is your weight in kg or lb? (kg/lb): ", ["kg", "lb"])
    weight = ask_float(f"Weight ({w_unit}): ")

    # Height
    h_unit = ask_choice("Is your height in cm or in? (cm/in): ", ["cm", "in"])
    height = ask_float(f"Height ({h_unit}): ")

    # Activity
    print("\nActivity levels:")
    print("  sedentary = little/no exercise")
    print("  light     = 1–3 days/wk")
    print("  moderate  = 3–5 days/wk")
    print("  very      = 6–7 days/wk")
    print("  athlete   = very hard exercise/physical job")
    activity = ask_choice("Choose activity (sedentary/light/moderate/very/athlete): ",
                          list(ACTIVITY_FACTORS.keys()))

    person = Person(
        sex=sex, age=age,
        weight=weight, weight_unit=w_unit,
        height=height, height_unit=h_unit,
        activity=activity
    )

    # Compute
    w_kg = person.weight_kg()
    h_cm = person.height_cm()
    bmr = bmr_mifflin_st_jeor(person.sex, w_kg, h_cm, person.age)
    tdee = tdee_from_bmr(bmr, person.activity)

    # Report in both unit systems for convenience
    print("\n--- Results ---")
    print(f"BMR (kcal/day): {bmr:.0f}")
    print(f"TDEE (kcal/day): {tdee:.0f}")
    print("\nFor reference:")
    print(f"  Weight: {w_kg:.1f} kg  ({kg_to_lbs(w_kg):.1f} lb)")
    print(f"  Height: {h_cm:.1f} cm  ({cm_to_inches(h_cm):.1f} in)")
    print(f"  Activity factor used: {ACTIVITY_FACTORS[activity]:.3f}")

if __name__ == "__main__":
    main()
