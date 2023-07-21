import webvtt
import requests
from io import StringIO
from datetime import datetime

def vtt_to_json(url, dedupe, single):
    "Convert WebVTT to JSON, optionally removing duplicate lines"
    vtt_text = requests.get(url).text
    captions = webvtt.read_buffer(StringIO(vtt_text))
    dicts = []
    prev_line = None
    for c in captions:
        if any("[closed captions are auto generated]" in l for l in c.lines):
            continue
        # Collect lines that are not dupes
        not_dupe_lines = []
        for line in c.lines:
            if not line.strip():
                continue
            if line != prev_line:
                not_dupe_lines.append(line)
            prev_line = line
        if not_dupe_lines:
            start = datetime.strptime(c.start, "%H:%M:%S.%f")
            end = datetime.strptime(c.end, "%H:%M:%S.%f")
            duration = (end - start).total_seconds()
            dicts.append({"start": start, "end": end, "duration": str(duration), "lines": " ".join(not_dupe_lines)})
    return dicts
