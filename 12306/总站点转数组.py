# build_stations.py —— 只跑一次
from pathlib import Path

src = Path("station_name.js.txt")   # 你那个文件
text = src.read_text(encoding="utf-8")

body = text.split("=", 1)[1].strip().strip("';\"")
rows = []
for item in body.split("@"):
    if not item:
        continue
    p = item.split("|")
    if len(p) < 5:
        continue
    # (中文名, 电报码, 全拼, 短拼音)
    rows.append((p[1], p[2], p[3], p[4]))

# 生成 stations_data.py
out = Path("stations_data.py")
with out.open("w", encoding="utf-8") as f:
    f.write("# 自动生成，勿手改。源：12306 station_name.js\n")
    f.write("STATIONS = [\n")
    for name, code, full, short in rows:
        f.write(f"    ({name!r}, {code!r}, {full!r}, {short!r}),\n")
    f.write("]\n")

print(f"已生成 {out}，共 {len(rows)} 条")