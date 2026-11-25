"""
import_ais.py - import cleaned AIS files into the PostgreSQL database.

Usage (in a terminal):
    python import_ais.py "C:\\path\\to\\ais-data\\cleaned" static
    python import_ais.py "C:\\path\\to\\ais-data\\cleaned" position

The last word decides which data are imported: static, position or all
(all is used if you leave it out).

Before you run it:
  * Install the database driver once:   pip install psycopg2-binary
  * Run clean_ais.py first. This script imports the cleaned files.
  * Create the table(s) with the SQL in the assignment.
  * Check the connection settings below (DATABASE).

The script:
  * finds all files ending in _CLEAN.csv in the folder and its subfolders
  * reads the header row of each file and translates the column names in the
    file to the column names in the table (e.g. dsrc -> data_source)
  * checks that the table has all the columns it needs, before importing
  * loads each file with PostgreSQL's COPY command, which is much faster than
    inserting the rows one by one
  * imports each file in its own transaction: if one file fails, the others
    are still imported, and the failed file leaves nothing behind

You will be asked for your PostgreSQL password when the script starts.
"""

import csv
import getpass
import os
import sys

try:
    import psycopg2
except ImportError:
    print("The package psycopg2 is missing. Install it with:\n    pip install psycopg2-binary")
    sys.exit(1)


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

# ---------------------------------------------------------------- settings

DATABASE = {
    "dbname": "ingof3205",
    "user": "postgres",
    "host": "localhost",
    "port": 5432,
}

TABLES = {"position": "ais_data.dynamic_ships", "static": "ais_data.static_ships"}

# Column name in the file -> column name in the table
COLUMN_NAMES = {
    "position": {
        "date_time_utc": "timestamp_utc", "mmsi": "mmsi",
        "dsrc": "data_source", "data_source": "data_source",
        "lon": "lon", "longitude": "lon", "lat": "lat", "latitude": "lat",
        "status": "status", "rate_of_turn": "rate_of_turn",
        "speed": "speed", "speed_over_ground": "speed",
        "course_over_ground": "course", "true_heading": "heading",
        "ais_class": "ais_class", "maneuvre": "maneuvre", "msg_type": "msg_type",
        "geometry": "geom",
    },
    "static": {
        "mmsi": "sourcemmsi", "date_time_utc": "timestamp_utc", "msg_type": "msg_type",
        "call_sign": "callsign", "ship_name": "shipname", "ship_type": "shiptype",
        "to_bow": "to_bow", "to_stern": "to_stern", "to_port": "to_port",
        "to_starboard": "to_starboard", "length": "length", "breadth": "breadth",
        "ais_class": "ais_class", "is_public": "is_public", "imo": "imo",
        "draught": "draught", "destination": "destination",
        "dsrc": "data_source", "data_source": "data_source",
    },
}

# ---------------------------------------------------------------- helpers


def read_header(path):
    with open(path, encoding="utf-8", errors="replace", newline="") as f:
        return [c.strip().lower() for c in next(csv.reader(f), [])]


def data_kind(columns):
    if any(c in columns for c in ("ship_name", "call_sign", "ship_type")):
        return "static"
    if any(c in columns for c in ("lat", "latitude")):
        return "position"
    return None


class Progress:
    """Wraps a file while COPY reads it: shows how far it has come, counts the
    rows, and remembers whether the user pressed Ctrl+C."""

    def __init__(self, f, name, total_bytes):
        self.f, self.name, self.total = f, name, max(total_bytes, 1)
        self.read_bytes, self.lines, self.shown, self.interrupted = 0, 0, -1, False

    def read(self, size=-1):
        try:
            data = self.f.read(size)
        except KeyboardInterrupt:
            self.interrupted = True
            raise
        self.read_bytes += len(data.encode("utf-8", errors="replace"))
        self.lines += data.count("\n")
        percent = int(100 * self.read_bytes / self.total)
        if percent != self.shown and percent % 5 == 0:
            self.shown = percent
            print(f"\r  {self.name}: {percent:3d} %", end="", flush=True)
        return data

    def readline(self, size=-1):
        return self.read(size) if size and size > 0 else self.f.readline()


def table_columns(cur, table):
    schema, name = table.split(".")
    cur.execute("SELECT column_name FROM information_schema.columns "
                f"WHERE table_schema = '{schema}' AND table_name = '{name}'")
    return {row[0] for row in cur.fetchall()}


def table_has_rows(cur, table):
    cur.execute(f"SELECT EXISTS (SELECT 1 FROM {table} LIMIT 1)")
    return cur.fetchone()[0]


# ---------------------------------------------------------------- main


def main():
    if len(sys.argv) not in (2, 3):
        print(__doc__)
        sys.exit(1)
    folder = folder_argument(sys.argv[1])
    only = sys.argv[2].lower() if len(sys.argv) == 3 else "all"
    if only not in ("static", "position", "all"):
        print(f"Unknown data type '{only}'. Use static, position or all.")
        sys.exit(1)

    files = sorted(os.path.join(d, f) for d, _, fs in os.walk(folder)
                   for f in fs if f.endswith("_CLEAN.csv"))
    if not files:
        print(f"No files ending in _CLEAN.csv found in {folder}.\n"
              "Run clean_ais.py first, and give the path to the 'cleaned' folder.")
        sys.exit(1)

    # Work out the type and the column list of each file
    jobs = []
    for path in files:
        header = read_header(path)
        kind = data_kind(header)
        name = os.path.basename(path)
        if kind is None:
            print(f"Skipping {name}: no recognisable header row. Run clean_ais.py first.")
            continue
        if only not in ("all", kind):
            continue
        unknown = [c for c in header if c not in COLUMN_NAMES[kind]]
        if unknown:
            print(f"Skipping {name}: unknown columns {unknown}. Add them to COLUMN_NAMES.")
            continue
        jobs.append((path, kind, [COLUMN_NAMES[kind][c] for c in header]))
    if not jobs:
        print(f"No {only} files to import in {folder}.")
        sys.exit(1)

    password = os.environ.get("PGPASSWORD") or getpass.getpass(
        f"PostgreSQL password for user '{DATABASE['user']}': ")
    try:
        conn = psycopg2.connect(password=password, **DATABASE)
    except psycopg2.OperationalError as e:
        print(f"Could not connect to the database:\n{e}")
        sys.exit(1)
    conn.set_client_encoding("UTF8")
    cur = conn.cursor()

    # Check each table before importing anything into it
    for kind in sorted({k for _, k, _ in jobs}):
        table = TABLES[kind]
        existing = table_columns(cur, table)
        needed = {c for _, k, cols in jobs if k == kind for c in cols}
        if not existing:
            print(f"\nThe table {table} does not exist. Create it with the SQL in the assignment.")
            jobs = [j for j in jobs if j[1] != kind]
            continue
        missing = sorted(needed - existing)
        if missing:
            print(f"\nThe table {table} is missing the columns {missing}.\n"
                  "Check that it was created with the SQL in the assignment.")
            jobs = [j for j in jobs if j[1] != kind]
            continue
        if table_has_rows(cur, table):
            try:
                answer = input(f"\n{table} already contains data. Importing again gives "
                               "duplicate rows. Continue anyway? [y/N] ")
            except EOFError:
                answer = ""
            if answer.strip().lower() != "y":
                jobs = [j for j in jobs if j[1] != kind]

    print(f"\nImporting {len(jobs)} files into {DATABASE['dbname']}")
    print("Each file is saved when it is complete. The rows are not visible in the table")
    print("until then. A day of position data takes a few minutes. Press Ctrl+C to stop.\n")
    imported, failed, done = 0, [], 0
    try:
        for path, kind, columns in jobs:
            table = TABLES[kind]
            name = os.path.basename(path)
            sql = f"COPY {table} ({', '.join(columns)}) FROM STDIN WITH (FORMAT csv, HEADER true)"
            progress = None
            try:
                with open(path, encoding="utf-8", errors="replace") as f:
                    progress = Progress(f, name, os.path.getsize(path))
                    cur.copy_expert(sql, progress)
                conn.commit()
                rows = progress.lines - 1          # minus the header row
                imported += rows
                done += 1
                print(f"\r  {name} -> {table}: {rows:,} rows")
            except psycopg2.Error as e:
                conn.rollback()
                if (progress is not None and progress.interrupted) or "KeyboardInterrupt" in str(e):
                    raise KeyboardInterrupt
                failed.append(name)
                print(f"\r  {name}: FAILED, nothing imported from this file\n      {str(e).strip()}")
    except KeyboardInterrupt:
        try:
            conn.rollback()
        except psycopg2.Error:
            pass
        print(f"\n\nStopped. The file being imported was rolled back; the {done} files "
              "finished before it are saved.\nTo start again, empty the table in pgAdmin first "
              "(this also frees the disk space):\n    TRUNCATE " + ", ".join(sorted({TABLES[k] for _, k, _ in jobs})) + ";")
        cur.close()
        conn.close()
        sys.exit(1)

    cur.close()
    conn.close()
    print(f"\nDone. Imported {imported:,} rows from {done} files.")
    if failed:
        print(f"{len(failed)} files failed: {', '.join(failed)}")


if __name__ == "__main__":
    main()
