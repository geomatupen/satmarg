from satoverpass import get_precise_overpasses

df = get_precise_overpasses(47.81306, 13.04667, '2025-02-01', '2025-02-10')
print(df)