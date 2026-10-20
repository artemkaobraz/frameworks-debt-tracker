-- 1. Все студенты
SELECT id, name, group_number FROM students ORDER BY name;

-- 2. Все дисциплины
SELECT id, name, teacher FROM disciplines ORDER BY name;

-- 3. Студенты заданной группы
SELECT id, name FROM students WHERE group_number = 'ЭФБО-02-24';

-- 4. Активные задолженности
SELECT id, student_id, discipline_id, date_created
FROM debts WHERE is_closed = 0;

-- 5. Задолженности с именами студентов и дисциплин
SELECT
    debts.id,
    students.name AS student_name,
    disciplines.name AS discipline_name,
    debts.date_created,
    debts.is_closed
FROM debts
JOIN students ON debts.student_id = students.id
JOIN disciplines ON debts.discipline_id = disciplines.id
ORDER BY debts.date_created;

-- 6. Студенты с их задолженностями
SELECT
    students.name AS student_name,
    disciplines.name AS discipline_name,
    debts.is_closed
FROM debts
JOIN students ON debts.student_id = students.id
JOIN disciplines ON debts.discipline_id = disciplines.id;

-- 7. Общее количество задолженностей
SELECT COUNT(*) AS total_debts FROM debts;

-- 8. Количество активных задолженностей
SELECT COUNT(*) AS active_debts FROM debts WHERE is_closed = 0;

-- 9. Количество задолженностей по студентам
SELECT
    students.name AS student_name,
    COUNT(debts.id) AS debts_count
FROM students
LEFT JOIN debts ON students.id = debts.student_id
GROUP BY students.id, students.name
ORDER BY debts_count DESC;

-- 10. Количество задолженностей по дисциплинам
SELECT
    disciplines.name AS discipline_name,
    COUNT(debts.id) AS debts_count
FROM disciplines
LEFT JOIN debts ON disciplines.id = debts.discipline_id
GROUP BY disciplines.id, disciplines.name
ORDER BY debts_count DESC;

-- 11. Студенты без активных задолженностей
SELECT students.id, students.name
FROM students
WHERE students.id NOT IN (
    SELECT debts.student_id FROM debts WHERE debts.is_closed = 0
)
ORDER BY students.name;

-- 12. Студенты с более чем одной активной задолженностью
SELECT
    students.name AS student_name,
    COUNT(debts.id) AS debts_count
FROM students
JOIN debts ON students.id = debts.student_id
WHERE debts.is_closed = 0
GROUP BY students.id, students.name
HAVING COUNT(debts.id) > 1
ORDER BY debts_count DESC;
