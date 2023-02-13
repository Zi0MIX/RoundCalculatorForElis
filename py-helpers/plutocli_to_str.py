with open("C:\\Users\\Zi0\\GitHub\\ZM-RoundCalculator\\analysis\\semtex_dmg.txt", "r", encoding="utf-8") as txt_io:
    txt_content = txt_io.readlines()

dmg_vals, distance_vals = [], []
for line in txt_content:
    dmg, dist = line.replace("[script]: ", "").replace("\n", "").split(" @ ")
    dmg_vals.append(dmg)
    distance_vals.append(dist)

print(f'"{" ".join(distance_vals)}"')
print()
print(f'"{" ".join(dmg_vals)}"')