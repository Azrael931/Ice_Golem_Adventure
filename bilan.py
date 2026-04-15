from codecarbon import EmissionsTracker

def bilan_carbone(func, *args, **kwargs):
    tracker = EmissionsTracker()
    tracker.start()

    result = func(*args, **kwargs)

    emissions = tracker.stop()
    print(f"🌍 Émissions carbone : {emissions:.6f} kg CO₂eq")

    return result

from bilan import bilan_carbone

def ma_fonction():
    total = 0
    for i in range(3_000_000):
        total += i
    return total

bilan_carbone(ma_fonction)
