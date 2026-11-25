
# Scripts

Two scripts for getting the AIS data from Kystverket into the database: first clean the files, then import them.

| Script | What it does | Needs |
|---|---|---|
| `clean_ais.py` | Removes invalid rows from the CSV files and writes cleaned copies | Python 3 only |
| `import_ais.py` | Loads the cleaned files into PostgreSQL | Python 3 and `psycopg2-binary` |

## The folder structure

The data from Kystverket come in one folder for position data and one for static data, with one subfolder per day:

```text
ais-data/
├── position/
│   ├── date_utc=2025-10-01/
│   │   ├── part-00001-tid-....c000.csv
│   │   ├── _SUCCESS
│   │   └── ...
│   └── date_utc=2025-10-02/ ...
└── static/
    ├── date_utc=2025-10-01/ ...
    └── ...
```

Both scripts search all the subfolders, so you only need to give them the `ais-data` folder. The helper files (`_SUCCESS`, `_started_...`, `_committed_...`) are ignored.

## 1. Clean the files

```bash
python clean_ais.py "C:\path\to\ais-data"
```

The script reads the header row of each file and recognises the columns by name, so it works even if the columns come in a different order. It works out by itself whether a file contains position data or static data. The current files from Kystverket look like this:

```text
position: date_time_utc,mmsi,dsrc,lon,lat,status,rate_of_turn,speed,course_over_ground,true_heading,ais_class
static:   mmsi,date_time_utc,msg_type,call_sign,ship_name,ship_type,to_bow,to_stern,to_port,to_starboard,length,breadth,ais_class,is_public,imo,draught,destination,dsrc
```

Cleaning takes about 35 seconds per day of position data (around 10 million rows), so the whole of October takes about 20 minutes. For each file the script:

1. **removes the row** if one of the essential values is wrong, since the row is useless without them:
   * wrong number of fields
   * missing or invalid timestamp or MMSI
   * missing or invalid position (`lon`/`lat`), or a position far outside the area
2. **empties the value** (and keeps the row) if another value is outside the allowed range, for example a course of 400, a heading of 600 or an IMO number written as `IMO9123456`. This way a valid position is not lost because of one bad value. The emptied values become `NULL` in the database. The rest of the row is kept exactly as it was.
3. writes the rows that are kept to the folder `ais-data/cleaned`, with names such as `position_2025-10-01_CLEAN.csv` and `static_2025-10-01_CLEAN.csv`. The rows are written exactly as they were, except that quotes inside text values are converted from the form Spark uses (`\"`) to the standard CSV form (`""`) that PostgreSQL expects. The original files are never changed.
4. prints how many rows were removed and how many values were emptied, and why.

**What the script does not do, on purpose:**

* It does **not** remove duplicate rows. You will count them yourself in the assignment.
* It does **not** remove the special values that mean "not available": course `360`, heading `511` and speed `102.3`. They are valid AIS values, and removing the row would also remove a valid position. Handle them in your SQL queries instead.

## 2. Import the files

Install the database driver once:

```bash
pip install psycopg2-binary
```

Create the table with the SQL in the assignment, and give the script the `cleaned` folder and the type of data to import:

```bash
python import_ais.py "C:\path\to\ais-data\cleaned" static
python import_ais.py "C:\path\to\ais-data\cleaned" position
```

Use `static` when you have created `ais_data.static_ships`, and `position` when you have created `ais_data.dynamic_ships`. If you leave out the last word, both are imported.

You will be asked for your PostgreSQL password. The script:

* finds all files ending in `_CLEAN.csv` in the folder, and translates the column names in the file to the names in the table (e.g. `dsrc` → `data_source`, `course_over_ground` → `course`)
* checks that the table has all the columns it needs before importing anything
* loads each file into the right table with PostgreSQL's `COPY` command
* imports each file in its own transaction: if a file fails, nothing from that file is imported, and the script continues with the next one
* warns you if the table already contains data, since importing the same files twice gives duplicate rows
* shows how far it has come with each file. The rows only become visible in the table when a whole file is finished, which takes a few minutes for a day of position data
* stops cleanly if you press Ctrl+C: the file being imported is rolled back, and the files finished before it are kept

If your database, user or port is not `ingof3205`, `postgres` and `5432`, change the settings in `DATABASE` at the top of `import_ais.py`.

## Windows and Mac

The scripts work the same way on both. The differences are in the terminal:

| | Windows | Mac |
|---|---|---|
| Run Python | `py clean_ais.py ...` or `python clean_ais.py ...` | `python3 clean_ais.py ...` |
| Install the driver | `py -m pip install psycopg2-binary` | `python3 -m pip install psycopg2-binary` |
| Example path | `"C:\data\ais-data"` | `~/Documents/ais-data` |

* **Put quotes around the path** if it contains spaces. Drag the folder into the terminal window to get the full path.
* **Windows:** Keep the data outside OneDrive (e.g. in `C:\data`). Files that are only stored online are downloaded one by one while the script reads them, which makes it very slow. Also keep the path short: the file names in the dataset are long, and Windows can have problems with paths over 260 characters.
* **Mac:** Hidden helper files from macOS (`._part-...` and `__MACOSX`) are ignored.
* **Line endings:** The cleaned files always use the same line endings, also if a file has been opened and saved on Windows.
* **Password:** If the password prompt does not work in your terminal (e.g. in some editors), set the environment variable `PGPASSWORD` before running the script.
* **psycopg2-binary will not install:** It is usually because your Python version is too new for the driver. Install the previous Python version (e.g. 3.12 or 3.13) and try again.

## Troubleshooting

| Message | What to do |
|---|---|
| `The package psycopg2 is missing` | Run `pip install psycopg2-binary` |
| `Could not connect to the database` | Check that PostgreSQL is running, and the password and settings in `DATABASE` |
| `The table ... does not exist` | Run the `CREATE TABLE` statement from the assignment first |
| `The table ... is missing the columns [...]` | The table was created with an older version of the SQL. Drop it (`DROP TABLE ais_data.dynamic_ships;`) and create it again with the SQL in the assignment |
| `wrong number of fields` for every row | The files have a format the script does not know. Send the first three lines of a file (`head -n 3 file.csv`) to your teacher |
| `invalid input syntax for type ...` | A value does not fit the column type. Check that the table was created with the SQL in the assignment, and that you are importing the files from the `cleaned` folder |
| The database grows, but the table is empty | The import is still working on the first file: rows are only visible when a file is finished. If you stopped the import, run `TRUNCATE ais_data.dynamic_ships;` to free the space before you start again |
| `python` is not recognised (Windows) | Use `py` instead of `python`, or reinstall Python with *Add python.exe to PATH* ticked |


## import_dynamic and import_status.sh
Bash script that iterates through CSV files in a specific directory and uses the psql command line tool to import data from each file into a PostgreSQL database table (ais_data.dynamic_ships or ais_statis_ships). This script is a straightforward way to bulk import CSV data into a PostgreSQL table directly from the command line.
