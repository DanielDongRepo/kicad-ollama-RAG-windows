import json
import sys
import os

# 强制将所有输出写入文件（绕过控制台静默）
log_file = open("script_debug.log", "w", buffering=1)
sys.stdout = log_file
sys.stderr = log_file

try:
    import pcbnew

    print("✅ pcbnew 导入成功")
except Exception as e:
    print(f"❌ pcbnew 导入失败: {e}")

# 在处理 PCB 文件时
print(f"正在加载文件: {sys.argv[1]}")


def extract_pcb_data(pcb_path):
    if not os.path.exists(pcb_path):
        raise FileNotFoundError(f"PCB 文件不存在: {pcb_path}")

    print(f"正在加载 KiCad 文件: {pcb_path}")
    board = pcbnew.LoadBoard(pcb_path)

    data = {"tracks": [], "vias": [], "components": [], "nets": set()}

    for track in board.GetTracks():
        if isinstance(track, pcbnew.PCB_TRACK):
            width_mm = track.GetWidth() / 1e6
            netname = track.GetNetname()
            data["tracks"].append({"width_mm": round(width_mm, 3), "net": netname})
            if netname:
                data["nets"].add(netname)
        elif isinstance(track, pcbnew.PCB_VIA):
            size_mm = track.GetWidth() / 1e6
            drill_mm = track.GetDrillValue() / 1e6
            data["vias"].append({"size_mm": round(size_mm, 3), "drill_mm": round(drill_mm, 3)})

    for fp in board.GetFootprints():
        ref = fp.GetReference()
        value = fp.GetValue()
        pos = fp.GetPosition()
        data["components"].append({
            "ref": ref,
            "value": value,
            "x_mm": round(pos.x / 1e6, 2),
            "y_mm": round(pos.y / 1e6, 2)
        })

    data["nets"] = list(data["nets"])
    return data


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(" 用法: python extract_pcb.py <your_board.kicad_pcb>")
        sys.exit(1)

    pcb_file = sys.argv[1]
    print(f" 正在加载 PCB 文件: {pcb_file}")
    extracted = extract_pcb_data(pcb_file)

    with open("pcb_data.json", "w", encoding="utf-8") as f:
        json.dump(extracted, f, indent=2, ensure_ascii=False)

    print(f"\n数据已保存到 pcb_data.json")
    print(f"走线数: {len(extracted['tracks'])}, 元件数: {len(extracted['components'])}")

    log_file.close()
