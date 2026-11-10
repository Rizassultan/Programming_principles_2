CREATE OR REPLACE FUNCTION search_contacts(pattern VARCHAR)
RETURNS TABLE(id INT, first_name VARCHAR, last_name VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY 
    SELECT c.id, c.first_name, c.last_name, c.phone 
    FROM contacts c
    WHERE c.first_name ILIKE '%' || pattern || '%'
       OR COALESCE(c.last_name, '') ILIKE '%' || pattern || '%'
       OR c.phone LIKE '%' || pattern || '%';
END;
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION insert_many_contacts(
    p_first_names VARCHAR[],
    p_last_names VARCHAR[],
    p_phones VARCHAR[]
)
RETURNS TABLE(failed_name VARCHAR, failed_phone VARCHAR, reason VARCHAR) AS $$
DECLARE
    i INT;
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
            ON CONFLICT (phone) DO NOTHING;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION get_contacts_paginated(p_limit INT, p_offset INT)
RETURNS TABLE(id INT, first_name VARCHAR, last_name VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY 
    SELECT c.id, c.first_name, c.last_name, c.phone 
    FROM contacts c
    ORDER BY c.id
    LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;