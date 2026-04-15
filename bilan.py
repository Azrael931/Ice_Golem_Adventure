from codecarbon import EmissionsTracker

def bilan_carbone(func, *args, **kwargs):
    tracker = EmissionsTracker(log_level="error")
    tracker.start()

    result = func(*args, **kwargs)

    emissions = tracker.stop()
    print(f"\n🌍 Bilan Carbone de la session : {emissions:.6f} kg CO₂eq\n")

    return result



if __name__ == "__main__":
    def ma_fonction():
        total = 0
        for i in range(3_000_000):
            total += i
        return total

    bilan_carbone(ma_fonction)
