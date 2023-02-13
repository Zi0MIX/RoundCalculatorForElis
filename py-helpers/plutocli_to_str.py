with open("C:\\Users\\Zi0\\GitHub\\ZM-RoundCalculator\\analysis\\semtex_dmg.txt", "r", encoding="utf-8") as txt_io:
    txt_content = txt_io.readlines()

dmg_vals, distance_vals = [], []
for line in txt_content:
    dmg, dist = line.replace("[script]: ", "").replace("\n", "").split(" @ ")
    dmg_vals.append(int(dmg))
    distance_vals.append(float(dist))

print(f'"{" ".join([str(x) for x in distance_vals])}"')
print()
print(f'"{" ".join([str(x) for x in dmg_vals])}"')
print()

avg_dist = sum(distance_vals) / len(distance_vals)
avg_dmg = sum(dmg_vals) / len(dmg_vals)
print(f"avg distance: {avg_dist} | avg damage: {avg_dmg}")