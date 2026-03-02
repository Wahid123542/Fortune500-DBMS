# Fortune 500 Database Engine

A file-based database management system built from scratch in Python for Fortune 500 company data. Built as a course assignment for Database Management Systems at the University of Arkansas.

Rather than using an existing database like SQLite or PostgreSQL, this project implements the core storage and retrieval logic manually — including fixed-length record design, direct file seeking, and a two-area search model.

---

## Features

- Create a database from a CSV file
- Open and close the database with persistent state
- Search for any company by name
- Add, update, and delete records
- Print a formatted report of the first 10 records

---

## Technical Design

### Fixed-Length Record Format (100 bytes per record)

| Field     | Size (bytes) |
|-----------|-------------|
| NAME      | 55          |
| RANK      | 4           |
| CITY      | 20          |
| STATE     | 2           |
| ZIP       | 10          |
| EMPLOYEES | 8           |
| Newline   | 1           |
| **Total** | **100**     |

Every record is exactly 100 bytes. This allows the program to jump directly to any record using:

```
position = record_number × 100
```

No need to scan the file sequentially — any record is one seek away.

### Two-Area Storage Model

The database splits records into two regions:

- **Sorted area** — the original 500 records loaded from CSV, stored in alphabetical order by company name. Supports **binary search (O(log n))**.
- **Overflow area** — new records appended to the end of the file. Searched with **linear search (O(n))**.

A config file tracks the count of sorted and unsorted records separately so the program knows which search to apply.

### Logical Deletion

When a record is deleted, the name field is preserved and all other fields are blanked out. This is intentional — removing the name would create a gap in alphabetical order and break binary search. The name acts as the primary key and sort anchor.

---

## How to Run

```bash
python3 Database.py
```

You will see a menu:

```
==================================================
DATABASE MANAGEMENT SYSTEM
==================================================
1) Create new database
2) Open database
3) Close database
4) Display record
5) Update record
6) Print report to the screen
7) Add record
8) Delete record
9) Quit
==================================================
```

To get started, select **1** and enter `Fortune500` when prompted (requires `Fortune500.csv` to be in the same directory).

---

## Dataset

`Fortune500.csv` contains 500 records of Fortune 500 companies with the following fields: company name, rank, city, state, ZIP code, and number of employees.

---

## What I Learned

- How fixed-length records enable O(1) random access via file seeking
- The tradeoff between O(log n) binary search on sorted data vs O(n) linear search on unsorted data
- Why logical deletion matters for maintaining sort order and index integrity
- How a config file can persist database state across sessions without loading all data into memory
