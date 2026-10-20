CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    group_number TEXT NOT NULL,
    record_book TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS disciplines (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    teacher TEXT NOT NULL,
    semester INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS debts (
    id INTEGER PRIMARY KEY,
    student_id INTEGER NOT NULL,
    discipline_id INTEGER NOT NULL,
    date_created TEXT NOT NULL,
    is_closed INTEGER NOT NULL DEFAULT 0 CHECK (is_closed IN (0, 1)),
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (discipline_id) REFERENCES disciplines(id)
);
