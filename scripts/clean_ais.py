"""
clean_ais.py - clean AIS files from Kystverket before importing them into PostgreSQL. 

Usage (in a terminal):
    python clean_ais.py "C:\\path\\to\\ais-data"

The script:
  * searches the folder AND all its subfolders for .csv files. This handles the
    folder structure from Kystverket, with one subfolder per day:
        ais-data/position/date_utc=2025-10-01/part-00001-....csv
        ais-data/static/date_utc=2025-10-01/part-00001-....csv
    Helper files such as _SUCCESS, _started_... and _committed_... are ignored.
  * reads the header row of each file and recognises the columns by name, so it
    works even if the columns come in a different order
  * detects whether each file contains position data or static data
  * removes a row only if one of the essential values is missing or invalid:
    timestamp, MMSI, position (lon/lat) or geometry, or if the row has the
    wrong number of fields or a position far outside the area
  * empties other invalid values (e.g. a course of 400) instead of removing
    the row, so that a valid position is not lost. The emptied values become
    NULL in the database.
  * writes the rows that are kept to the folder "cleaned" inside the folder you
    gave, split into one subfolder per data type:
        cleaned/position/position_2025-10-01.csv
        cleaned/static/static_2025-10-01.csv
    The original files are never changed.
  * prints how many rows were removed and how many values were emptied, and why

What the script does NOT do (on purpose):
  * It does not remove duplicate rows. You will count them yourself (Task 5).
  * It does not remove the special values that mean "not available"
    (course 360, heading 511, speed 102.3). They are valid AIS values, and
    removing the whole row would also remove a valid position. Handle them
    in your SQL queries instead.

No extra Python packages are needed.
"""

import csv
import io
import os
import re
import sys
from collections import Counter
from datetime import datetime


def folder_argument(arg):
    """Clean up the folder given on the command line. On Windows, a path that
    ends with a backslash before the closing quote ("C:\\data\\") arrives with
    a stray quote at the end, so stray quotes and spaces are removed."""
    folder = arg.strip().strip('"').strip("'").strip()
    return os.path.normpath(os.path.expanduser(folder))


# Never crash on printing special characters (e.g. in a Windows console)
try:
    sys.stdout.reconfigure(errors="replace")
except AttributeError:
    pass

# Positions outside this box are removed. The box is wide on purpose: the
# dataset includes satellite data from vessels far from the coast.
LAT_MIN, LAT_MAX = 55.0, 90.0
LON_MIN, LON_MAX = -40.0, 70.0

# Column names used for files without a header row, chosen by the number of columns
HEADERLESS = {
    11: "date_time_utc,mmsi,dsrc,lon,lat,status,rate_of_turn,speed,"
        "course_over_ground,true_heading,ais_class",
    14: "date_time_utc,mmsi,longitude,latitude,status,course_over_ground,true_heading,"
        "speed_over_ground,rate_of_turn,maneuvre,data_source,ais_class,msg_type,geometry",
    18: "mmsi,date_time_utc,msg_type,call_sign,ship_name,ship_type,to_bow,to_stern,"
        "to_port,to_starboard,length,breadth,ais_class,is_public,imo,draught,destination,dsrc",
}


# ---------------------------------------------------------------- value checks

def is_int(value, lo=None, hi=None):
    try:
        number = int(value)
    except ValueError:
        return False
    return (lo is None or number >= lo) and (hi is None or number <= hi)


def is_float(value, lo=None, hi=None):
    try:
        number = float(value)
    except ValueError:
        return False
    return (lo is None or number >= lo) and (hi is None or number <= hi)


def is_timestamp(value):
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


# For each known column: (check function, may the value be empty?, reason if invalid)
CHECKS = {
    "date_time_utc":      (is_timestamp, False, "invalid timestamp"),
    "mmsi":               (lambda v: v.isdigit() and len(v) <= 9, False, "invalid MMSI"),
    "lon":                (lambda v: is_float(v, -180, 180), False, "invalid position"),
    "longitude":          (lambda v: is_float(v, -180, 180), False, "invalid position"),
    "lat":                (lambda v: is_float(v, -90, 90), False, "invalid position"),
    "latitude":           (lambda v: is_float(v, -90, 90), False, "invalid position"),
    "status":             (lambda v: is_int(v, 0, 15), True, "invalid navigational status"),
    "course_over_ground": (lambda v: is_float(v, 0, 360), True, "invalid course"),        # 360 = not available
    "true_heading":       (lambda v: is_int(v, 0, 359) or v == "511", True, "invalid heading"),  # 511 = not available
    "speed":              (lambda v: is_float(v, 0, 102.3), True, "invalid speed"),       # 102.3 = not available
    "speed_over_ground":  (lambda v: is_float(v, 0, 102.3), True, "invalid speed"),
    "rate_of_turn":       (is_float, True, "invalid rate of turn"),
    "maneuvre":           (is_int, True, "invalid manoeuvre indicator"),
    "msg_type":           (is_int, True, "invalid message type"),
    "geometry":           (lambda v: v.upper().startswith("POINT"), False, "invalid geometry"),
    "ship_type":          (lambda v: is_int(v, 0, 255), True, "invalid ship type"),
    "to_bow":             (lambda v: is_int(v, 0), True, "invalid antenna position"),
    "to_stern":           (lambda v: is_int(v, 0), True, "invalid antenna position"),
    "to_port":            (lambda v: is_int(v, 0), True, "invalid antenna position"),
    "to_starboard":       (lambda v: is_int(v, 0), True, "invalid antenna position"),
    "length":             (lambda v: is_float(v, 0), True, "invalid dimensions"),
    "breadth":            (lambda v: is_float(v, 0), True, "invalid dimensions"),
    "is_public":          (lambda v: v.lower() in ("true", "false"), True, "invalid is_public value"),
    "imo":                (lambda v: is_int(v, 0), True, "invalid IMO number"),
    "draught":            (lambda v: is_float(v, 0), True, "invalid draught"),
}


# Columns that the row cannot do without: an invalid value here removes the row.
# An invalid value in any other column is emptied instead.
ESSENTIAL = {"date_time_utc", "mmsi", "lon", "longitude", "lat", "latitude", "geometry"}


def make_checker(columns):
    """Build a function that checks one row, based on the column names in the header.
    It returns (reason, emptied): reason is set if the row must be removed;
    emptied lists (column index, reason) for values that must be emptied."""
    checks = [(i, name in ESSENTIAL, CHECKS[name]) for i, name in enumerate(columns) if name in CHECKS]
    lon_i = next((i for i, n in enumerate(columns) if n in ("lon", "longitude")), None)
    lat_i = next((i for i, n in enumerate(columns) if n in ("lat", "latitude")), None)
    n_cols = len(columns)

    def check(fields):
        if len(fields) != n_cols:
            return "wrong number of fields", []
        emptied = []
        for i, essential, (func, may_be_empty, reason) in checks:
            value = fields[i].strip()
            ok = may_be_empty if value == "" else func(value)
            if not ok:
                if essential:
                    return reason, []
                emptied.append((i, reason))
        if lon_i is not None and lat_i is not None:
            lon, lat = float(fields[lon_i]), float(fields[lat_i])
            if not (LON_MIN <= lon <= LON_MAX and LAT_MIN <= lat <= LAT_MAX):
                return "position outside the area", []
        return None, emptied

    return check


# ---------------------------------------------------------------- file handling

class LineRecorder:
    """Feeds lines to csv.reader and remembers the raw text of each record,
    so that the rows we keep can be written back exactly as they were."""

    def __init__(self, f):
        self.f = f
        self.buffer = []

    def __iter__(self):
        return self

    def __next__(self):
        line = next(self.f)
        self.buffer.append(line)
        return line

    def take(self):
        raw = "".join(self.buffer)
        self.buffer = []
        # Always end the row with \n, also if the file uses Windows line
        # endings (\r\n): mixed line endings make PostgreSQL reject the file.
        return raw.rstrip("\r\n") + "\n"


def normalise(fields, raw):
    """Spark writes quotes inside text as \\" instead of the standard "".
    PostgreSQL expects the standard form, so such rows are written out again
    in standard CSV. All other rows are kept exactly as they were."""
    if '\\"' not in raw:
        return raw
    out = io.StringIO()
    csv.writer(out, lineterminator="\n").writerow(fields)
    return out.getvalue()


def raw_tokens(raw):
    """Split one CSV line into its fields exactly as written (quotes included).
    Returns None if the line cannot be split safely (e.g. a field over several lines)."""
    line = raw.rstrip("\r\n")
    tokens, start, i, in_quotes = [], 0, 0, False
    while i < len(line):
        c = line[i]
        if in_quotes:
            if c == "\\":
                i += 1                      # skip the escaped character
            elif c == '"':
                if i + 1 < len(line) and line[i + 1] == '"':
                    i += 1                  # doubled quote inside a quoted field
                else:
                    in_quotes = False
        elif c == '"':
            in_quotes = True
        elif c == ",":
            tokens.append(line[start:i])
            start = i + 1
        i += 1
    if in_quotes:
        return None
    tokens.append(line[start:])
    return tokens


def empty_values(fields, raw, emptied):
    """Write the row again with the invalid values emptied, keeping everything
    else exactly as it was written in the file."""
    tokens = raw_tokens(raw) if '\\"' not in raw else None
    if tokens is not None and len(tokens) == len(fields):
        for i, _ in emptied:
            tokens[i] = ""
        return ",".join(tokens) + "\n"
    fields = list(fields)
    for i, _ in emptied:
        fields[i] = ""
    out = io.StringIO()
    csv.writer(out, lineterminator="\n").writerow(fields)
    return out.getvalue()


def find_csv_files(root):
    """All data CSV files under root, skipping the output folder and helper files."""
    found = []
    for folder, subfolders, files in os.walk(root):
        subfolders[:] = sorted(d for d in subfolders
                               if d.lower() != "cleaned" and not d.startswith((".", "_")))
        for f in sorted(files):
            low = f.lower()
            if low.endswith(".csv") and not f.startswith((".", "_")):
                found.append(os.path.join(folder, f))
    return found


def output_name(path, kind, parts_in_folder, used):
    """position_2025-10-01.csv, from the date_utc=... folder if there is one."""
    m = re.search(r"date_utc=([0-9-]+)", path.replace("\\", "/"))
    stem = os.path.splitext(os.path.basename(path))[0]
    if m:
        base = f"{kind}_{m.group(1)}"
        if parts_in_folder > 1:
            part = re.match(r"(part-\d+)", stem)
            base += "_" + (part.group(1) if part else stem)
    else:
        base = f"{kind}_{stem}"
    name, n = base, 2
    while name in used:
        name, n = f"{base}_{n}", n + 1
    used.add(name)
    return name + ".csv"


def read_header(first_fields):
    """Return (column names, has_header) for the first row of a file."""
    names = [f.strip().lower() for f in first_fields]
    if "date_time_utc" in names and "mmsi" in names:
        return names, True
    if len(first_fields) in HEADERLESS:
        return HEADERLESS[len(first_fields)].split(","), False
    return None, False


def data_kind(columns):
    if any(c in columns for c in ("ship_name", "call_sign", "ship_type")):
        return "static"
    if any(c in columns for c in ("lat", "latitude")):
        return "position"
    return None


def clean_file(path, out_folder, parts_in_folder, used_names, root):
    name = os.path.relpath(path, root)
    reasons = Counter()
    emptied_count = Counter()
    kept = 0

    with open(path, encoding="utf-8", errors="replace", newline="") as src:
        recorder = LineRecorder(src)
        reader = csv.reader(recorder, escapechar="\\")
        try:
            first = next(reader)
        except StopIteration:
            print(f"  {name}: empty file, skipped")
            return None
        first_raw = recorder.take()
        columns, has_header = read_header(first)
        kind = data_kind(columns) if columns else None
        if kind is None:
            print(f"  {name}: unknown format, skipped. First line:\n      {first_raw.strip()[:150]}")
            return None
        check = make_checker(columns)
        out_name = output_name(path, kind, parts_in_folder, used_names)
        kind_folder = os.path.join(out_folder, kind)
        os.makedirs(kind_folder, exist_ok=True)
        out_path = os.path.join(kind_folder, out_name)
        out_name = os.path.join(kind, out_name)     # shown in the summary

        with open(out_path, "w", encoding="utf-8", newline="") as dst:
            dst.write(",".join(columns) + "\n")
            rows = reader if has_header else _chain([(first, first_raw)], reader, recorder)
            for item in rows:
                if has_header:
                    fields, raw = item, recorder.take()
                else:
                    fields, raw = item
                if not fields:          # blank line
                    continue
                reason, emptied = check(fields)
                if reason:
                    reasons[reason] += 1
                    continue
                if emptied:
                    for _, why in emptied:
                        emptied_count[why] += 1
                    dst.write(empty_values(fields, raw, emptied))
                else:
                    dst.write(normalise(fields, raw))
                kept += 1

    removed = sum(reasons.values())
    print(f"  {name}\n    -> {out_name} ({kind} data): kept {kept:,} rows, removed {removed:,} rows, "
          f"emptied {sum(emptied_count.values()):,} values")
    for reason, count in reasons.most_common():
        print(f"      - row removed, {reason}: {count:,}")
    for reason, count in emptied_count.most_common():
        print(f"      - value emptied, {reason}: {count:,}")
    return kind, kept, reasons, emptied_count


def _chain(first_items, reader, recorder):
    """Yield (fields, raw) pairs: first the row already read, then the rest."""
    yield from first_items
    for fields in reader:
        yield fields, recorder.take()


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    folder = folder_argument(sys.argv[1])
    if not os.path.isdir(folder):
        print(f"Folder not found: {folder}")
        sys.exit(1)

    files = find_csv_files(folder)
    if not files:
        print(f"No CSV files found in {folder} or its subfolders")
        sys.exit(1)

    out_folder = os.path.join(folder, "cleaned")
    os.makedirs(out_folder, exist_ok=True)
    print(f"Cleaning {len(files)} files. Results are written to: {out_folder}\n")

    per_folder = Counter(os.path.dirname(f) for f in files)
    used_names = set()
    total_kept, total_reasons, total_emptied = 0, Counter(), Counter()
    for f in files:
        result = clean_file(f, out_folder, per_folder[os.path.dirname(f)], used_names, folder)
        if result:
            total_kept += result[1]
            total_reasons += result[2]
            total_emptied += result[3]

    print(f"\nDone. Kept {total_kept:,} rows, removed {sum(total_reasons.values()):,} rows, "
          f"emptied {sum(total_emptied.values()):,} values.")
    for reason, count in total_reasons.most_common():
        print(f"  - row removed, {reason}: {count:,}")
    for reason, count in total_emptied.most_common():
        print(f"  - value emptied, {reason}: {count:,}")


if __name__ == "__main__":
    main()
