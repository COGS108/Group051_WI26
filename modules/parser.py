import xml.etree.ElementTree as ET
import pandas as pd
from pathlib import Path


def safe_text(element):
    return element.text if element is not None else None


def convert_value(value):
    if value is None:
        return None

    try:
        if "." in value:
            return float(value)
        else:
            return int(value)
    except (ValueError, TypeError):
        return value


def parse_single_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    rows = []

    for entry in root.findall(".//HighScoreForASongAndSteps"):
        song = entry.find("Song")
        steps = entry.find("Steps")
        highscore = entry.find("HighScore")

        if highscore is None:
            continue

        row = {}

        row["song_dir"] = song.get("Dir") if song is not None else None
        row["difficulty"] = steps.get("Difficulty") if steps is not None else None
        row["steps_type"] = steps.get("StepsType") if steps is not None else None

        for child in highscore:
            if child.tag in ["TapNoteScores", "HoldNoteScores", "RadarValues"]:
                continue

            row[child.tag.lower()] = convert_value(child.text)

        tap_section = highscore.find("TapNoteScores")
        if tap_section is not None:
            for child in tap_section:
                col = f"tapnotescores_{child.tag.lower()}"
                row[col] = convert_value(child.text)

        hold_section = highscore.find("HoldNoteScores")
        if hold_section is not None:
            for child in hold_section:
                col = f"holdnotescores_{child.tag.lower()}"
                row[col] = convert_value(child.text)

        radar_section = highscore.find("RadarValues")
        if radar_section is not None:
            for child in radar_section:
                col = f"radarvalues_{child.tag.lower()}"
                row[col] = convert_value(child.text)

        rows.append(row)

    return rows


def parse_folder(folder_path):
    folder = Path(folder_path)
    all_rows = []

    for xml_file in folder.glob("*.xml"):
        print(f"Parsing {xml_file.name}")
        rows = parse_single_xml(xml_file)
        all_rows.extend(rows)

    return pd.DataFrame(all_rows)


if __name__ == "__main__":
    df = parse_folder("2026-2-14 animefest data")

    print(df.head())
    print("\nColumns:\n", df.columns.tolist())
    df.to_csv("parsed.csv")
