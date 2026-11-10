CREATE OR REPLACE PROCEDURE upsert_contact(p_first_name VARCHAR, p_last_name VARCHAR, p_phone VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM contacts WHERE first_name = p_first_name) THEN
        UPDATE contacts 
        SET phone = p_phone, last_name = p_last_name 
        WHERE first_name = p_first_name;
    ELSE
        INSERT INTO contacts(first_name, last_name, phone) 
        VALUES(p_first_name, p_last_name, p_phone);
    END IF;
END;
$$;



CREATE OR REPLACE PROCEDURE delete_contact_proc(p_identifier VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM contacts 
    WHERE first_name = p_identifier OR phone = p_identifier;
END;
$$;