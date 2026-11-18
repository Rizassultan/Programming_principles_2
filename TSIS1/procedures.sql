-- ==========================================
-- БАЗОВЫЕ ПРОЦЕДУРЫ И ФУНКЦИИ ИЗ PRACTICE 8
-- ==========================================

-- 1. Upsert контакта (обновлено так, чтобы номер сразу дублировался и в таблицу phones)
CREATE OR REPLACE PROCEDURE upsert_contact(p_first_name VARCHAR, p_last_name VARCHAR, p_phone VARCHAR)
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INT;
BEGIN
    IF EXISTS (SELECT 1 FROM contacts WHERE first_name = p_first_name) THEN
        UPDATE contacts 
        SET phone = p_phone, last_name = p_last_name 
        WHERE first_name = p_first_name
        RETURNING id INTO v_contact_id;
    ELSE
        INSERT INTO contacts(first_name, last_name, phone) 
        VALUES(p_first_name, p_last_name, p_phone)
        RETURNING id INTO v_contact_id;
    END IF;

    IF p_phone IS NOT NULL THEN
        INSERT INTO phones(contact_id, phone, type)
        VALUES (v_contact_id, p_phone, 'mobile')
        ON CONFLICT (contact_id, phone) DO NOTHING;
    END IF;
END;
$$;

-- 2. Удаление контакта по имени или любому его телефону
CREATE OR REPLACE PROCEDURE delete_contact_proc(p_identifier VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM contacts 
    WHERE first_name = p_identifier 
       OR phone = p_identifier
       OR id IN (SELECT contact_id FROM phones WHERE phone = p_identifier);
END;
$$;

-- 3. Массовая вставка с валидацией (Practice 8)
CREATE OR REPLACE FUNCTION insert_many_contacts(
    p_first_names VARCHAR[],
    p_last_names VARCHAR[],
    p_phones VARCHAR[]
)
RETURNS TABLE(failed_name VARCHAR, failed_phone VARCHAR, reason VARCHAR) AS $$
DECLARE
    i INT;
    v_id INT;
BEGIN
    FOR i IN 1 .. array_length(p_first_names, 1) LOOP
        IF p_phones[i] NOT LIKE '+%' OR length(p_phones[i]) < 10 THEN
            failed_name := p_first_names[i];
            failed_phone := p_phones[i];
            reason := 'Неверный формат номера';
            RETURN NEXT; 
        ELSE
            INSERT INTO contacts(first_name, last_name, phone)
            VALUES (p_first_names[i], p_last_names[i], p_phones[i])
            ON CONFLICT (phone) DO UPDATE SET first_name = EXCLUDED.first_name
            RETURNING id INTO v_id;

            INSERT INTO phones(contact_id, phone, type)
            VALUES (v_id, p_phones[i], 'mobile')
            ON CONFLICT (contact_id, phone) DO NOTHING;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- 4. Пагинация (Practice 8)
DROP FUNCTION IF EXISTS get_contacts_paginated(INT, INT);
CREATE OR REPLACE FUNCTION get_contacts_paginated(p_limit INT, p_offset INT)
RETURNS TABLE(
    id INT, 
    first_name VARCHAR, 
    last_name VARCHAR, 
    email VARCHAR, 
    birthday DATE, 
    group_name VARCHAR, 
    phones_list TEXT
) AS $$
BEGIN
    RETURN QUERY 
    SELECT 
        c.id, 
        c.first_name, 
        c.last_name, 
        c.email, 
        c.birthday, 
        g.name AS group_name,
        COALESCE(STRING_AGG(p.phone || ' (' || p.type || ')', ', '), c.phone, 'Нет номера') AS phones_list
    FROM contacts c
    LEFT JOIN groups g ON c.group_id = g.id
    LEFT JOIN phones p ON c.id = p.contact_id
    GROUP BY c.id, g.name
    ORDER BY c.id
    LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;


-- ==========================================
-- НОВЫЕ ПРОЦЕДУРЫ И ФУНКЦИИ ДЛЯ TSIS 1 (3.4)
-- ==========================================

-- 1. Процедура add_phone: добавляет новый номер существующему контакту
CREATE OR REPLACE PROCEDURE add_phone(p_contact_name VARCHAR, p_phone VARCHAR, p_type VARCHAR)
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INT;
BEGIN
    SELECT id INTO v_contact_id 
    FROM contacts 
    WHERE first_name ILIKE p_contact_name 
       OR (first_name || ' ' || COALESCE(last_name, '')) ILIKE p_contact_name
    LIMIT 1;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Контакт "%" не найден', p_contact_name;
    END IF;

    INSERT INTO phones (contact_id, phone, type)
    VALUES (v_contact_id, p_phone, LOWER(p_type))
    ON CONFLICT (contact_id, phone) DO UPDATE SET type = EXCLUDED.type;
END;
$$;

-- 2. Процедура move_to_group: переносит контакт в группу (создает группу, если её нет)
CREATE OR REPLACE PROCEDURE move_to_group(p_contact_name VARCHAR, p_group_name VARCHAR)
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INT;
    v_group_id INT;
BEGIN
    SELECT id INTO v_contact_id 
    FROM contacts 
    WHERE first_name ILIKE p_contact_name 
       OR (first_name || ' ' || COALESCE(last_name, '')) ILIKE p_contact_name
    LIMIT 1;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Контакт "%" не найден', p_contact_name;
    END IF;

    INSERT INTO groups (name)
    VALUES (p_group_name)
    ON CONFLICT (name) DO NOTHING;

    SELECT id INTO v_group_id FROM groups WHERE name = p_group_name;

    UPDATE contacts SET group_id = v_group_id WHERE id = v_contact_id;
END;
$$;

-- 3. Функция search_contacts(p_query TEXT): ищет по имени, фамилии, email и всем номерам в phones
DROP FUNCTION IF EXISTS search_contacts(VARCHAR);
DROP FUNCTION IF EXISTS search_contacts(TEXT);

CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE(
    id INT, 
    first_name VARCHAR, 
    last_name VARCHAR, 
    email VARCHAR, 
    birthday DATE, 
    group_name VARCHAR, 
    phones_list TEXT
) AS $$
BEGIN
    RETURN QUERY 
    SELECT 
        c.id, 
        c.first_name, 
        c.last_name, 
        c.email, 
        c.birthday, 
        g.name AS group_name,
        COALESCE(STRING_AGG(DISTINCT p.phone || ' (' || p.type || ')', ', '), c.phone, 'Нет номера') AS phones_list
    FROM contacts c
    LEFT JOIN groups g ON c.group_id = g.id
    LEFT JOIN phones p ON c.id = p.contact_id
    WHERE c.first_name ILIKE '%' || p_query || '%'
       OR COALESCE(c.last_name, '') ILIKE '%' || p_query || '%'
       OR COALESCE(c.email, '') ILIKE '%' || p_query || '%'
       OR COALESCE(c.phone, '') ILIKE '%' || p_query || '%'
       OR EXISTS (
           SELECT 1 FROM phones p2 
           WHERE p2.contact_id = c.id AND p2.phone ILIKE '%' || p_query || '%'
       )
    GROUP BY c.id, g.name
    ORDER BY c.id;
END;
$$ LANGUAGE plpgsql;