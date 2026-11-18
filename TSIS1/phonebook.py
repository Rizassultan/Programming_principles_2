from connect import get_connection
import csv
import json

def create_table():
    conn = get_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            with open('schema.sql', 'r', encoding='utf-8') as f:
                cursor.execute(f.read())
            conn.commit()
            cursor.close()
            print("Схема БД (schema.sql) успешно загружена и обновлена!")
        except Exception as error:
            print("Ошибка при обновлении схемы:", error)
        finally:
            conn.close()                 

def create_db_functions():
    conn = get_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            with open('procedures.sql', 'r', encoding='utf-8') as f:
                cursor.execute(f.read())
            conn.commit()
            cursor.close()
            print("Процедуры и функции (procedures.sql) успешно загружены в базу!")
        except Exception as error:
            print("Ошибка при загрузке procedures.sql:", error)
        finally:
            conn.close()



def insert_from_csv(filename):
    """Расширенный импорт из CSV (3.3.3) с сохранением валидации из Practice 8"""
    sql_call = "SELECT * FROM insert_many_contacts(%s::VARCHAR[], %s::VARCHAR[], %s::VARCHAR[]);"
    
    conn = get_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            first_names, last_names, phones = [], [], []
            extra_data = []
            
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader, None)
                for row in reader:
                    if not row or len(row) < 3:
                        continue
                    fn = row[0].strip()
                    ln = row[1].strip()
                    ph = row[2].strip()
                    p_type = row[3].strip().lower() if len(row) > 3 and row[3].strip() else 'mobile'
                    email = row[4].strip() if len(row) > 4 and row[4].strip() else None
                    bday = row[5].strip() if len(row) > 5 and row[5].strip() else None
                    grp = row[6].strip() if len(row) > 6 and row[6].strip() else None
                    
                    first_names.append(fn)
                    last_names.append(ln)
                    phones.append(ph)
                    extra_data.append((fn, ph, p_type, email, bday, grp))
            
            cursor.execute(sql_call, (first_names, last_names, phones))
            bad_data = cursor.fetchall()
            bad_phones = {b[1] for b in bad_data}
            
            # Обновляем расширенные поля для всех контактов, прошедших валидацию
            for fn, ph, p_type, email, bday, grp in extra_data:
                if ph not in bad_phones:
                    cursor.execute("""
                        UPDATE contacts 
                        SET email = COALESCE(%s, email),
                            birthday = COALESCE(%s::DATE, birthday)
                        WHERE first_name = %s;
                    """, (email, bday, fn))
                    
                    if p_type in ('home', 'work', 'mobile'):
                        cursor.execute("CALL add_phone(%s, %s, %s);", (fn, ph, p_type))
                    if grp:
                        cursor.execute("CALL move_to_group(%s, %s);", (fn, grp))
            
            conn.commit()
            
            print(f"\n--- Отчет по файлу {filename} ---")
            if bad_data:
                print("ВНИМАНИЕ! Эти контакты НЕ добавлены (ошибка валидации):")
                for bad in bad_data:
                    print(f"Имя: {bad[0]} | Тел: {bad[1]} | Ошибка: {bad[2]}")
                print("Остальные контакты успешно загружены со всеми полями.")
            else:
                print("Все контакты успешно добавлены без ошибок!")
            print("----------------------------------\n")
                
            cursor.close()
        except Exception as error:
            print("Ошибка при загрузке из CSV:", error)
        finally:
            conn.close()


def export_to_json(filename="contacts.json"):
    """Экспорт всех контактов (включая список телефонов и группу) в JSON (3.3.1)"""
    conn = get_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.id, c.first_name, c.last_name, c.email, c.birthday, g.name
                FROM contacts c
                LEFT JOIN groups g ON c.group_id = g.id
                ORDER BY c.id;
            """)
            contacts_rows = cursor.fetchall()
            
            export_list = []
            for row in contacts_rows:
                c_id, fn, ln, email, bday, grp = row
                cursor.execute("SELECT phone, type FROM phones WHERE contact_id = %s;", (c_id,))
                phones_rows = cursor.fetchall()
                phones_data = [{"phone": p[0], "type": p[1]} for p in phones_rows]
                
                export_list.append({
                    "first_name": fn,
                    "last_name": ln,
                    "email": email,
                    "birthday": str(bday) if bday else None,
                    "group": grp,
                    "phones": phones_data
                })
                
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_list, f, ensure_ascii=False, indent=4)
                
            print(f"Экспортировано {len(export_list)} контактов в файл '{filename}'!")
            cursor.close()
        except Exception as error:
            print("Ошибка при экспорте в JSON:", error)
        finally:
            conn.close()


def import_from_json(filename="contacts.json"):
    """Импорт контактов из JSON с обработкой дубликатов skip / overwrite (3.3.2)"""
    conn = get_connection()
    if conn is not None:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            cursor = conn.cursor()
            imported_count = 0
            
            for item in data:
                fn = item.get("first_name")
                if not fn:
                    continue
                ln = item.get("last_name")
                email = item.get("email")
                bday = item.get("birthday")
                grp = item.get("group")
                phones = item.get("phones", [])
                
                cursor.execute("SELECT id FROM contacts WHERE first_name = %s LIMIT 1;", (fn,))
                existing = cursor.fetchone()
                
                if existing:
                    c_id = existing[0]
                    while True:
                        ans = input(f"Контакт '{fn}' уже существует. [s]kip (пропустить) или [o]verwrite (перезаписать)? ").strip().lower()
                        if ans in ('s', 'skip', 'o', 'overwrite'):
                            break
                        print("Введите 's' или 'o'.")
                        
                    if ans in ('s', 'skip'):
                        print(f"Пропущен контакт '{fn}'.")
                        continue
                    else:
                        first_phone = phones[0]["phone"] if phones else None
                        cursor.execute("""
                            UPDATE contacts 
                            SET last_name = %s, phone = %s, email = %s, birthday = %s::DATE
                            WHERE id = %s;
                        """, (ln, first_phone, email, bday, c_id))
                        cursor.execute("DELETE FROM phones WHERE contact_id = %s;", (c_id,))
                else:
                    first_phone = phones[0]["phone"] if phones else None
                    cursor.execute("""
                        INSERT INTO contacts (first_name, last_name, phone, email, birthday)
                        VALUES (%s, %s, %s, %s, %s::DATE)
                        RETURNING id;
                    """, (fn, ln, first_phone, email, bday))
                    c_id = cursor.fetchone()[0]
                
                if grp:
                    cursor.execute("CALL move_to_group(%s, %s);", (fn, grp))
                    
                for p in phones:
                    p_num = p.get("phone")
                    p_type = p.get("type", "mobile").lower()
                    if p_num and p_type in ('home', 'work', 'mobile'):
                        cursor.execute("CALL add_phone(%s, %s, %s);", (fn, p_num, p_type))
                        
                imported_count += 1
                
            conn.commit()
            print(f"Импорт из '{filename}' завершен! Обработано контактов: {imported_count}.")
            cursor.close()
        except Exception as error:
            print("Ошибка при импорте из JSON:", error)
        finally:
            conn.close()


def print_contacts_table(rows, title="Список контактов"):
    """Вспомогательная функция для красивого вывода контактов со всеми новыми полями"""
    print(f"\n--- {title} ---")
    if not rows:
        print("Ничего не найдено.")
    else:
        print(f"{'ID':<4} | {'Имя и Фамилия':<22} | {'Email':<22} | {'Д.Р.':<10} | {'Группа':<10} | {'Телефоны'}")
        print("-" * 105)
        for row in rows:
            c_id = row[0]
            full_name = f"{row[1]} {row[2] or ''}".strip()
            email = row[3] or "-"
            bday = str(row[4]) if row[4] else "-"
            group = row[5] or "-"
            phones = row[6] or "-"
            print(f"{c_id:<4} | {full_name:<22} | {email:<22} | {bday:<10} | {group:<10} | {phones}")
    print("-" * 105 + "\n")


def query_contacts(search_term=""):
    """Поиск через новую функцию search_contacts (ищет по имени, email и всем телефонам)"""
    sql_query = "SELECT * FROM search_contacts(%s);"
    conn = get_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute(sql_query, (search_term,))
            rows = cursor.fetchall()
            print_contacts_table(rows, f"Результаты поиска по '{search_term}'")
            cursor.close()
        except Exception as error:
            print("Ошибка при поиске:", error)
        finally:
            conn.close()


def add_extra_phone(contact_name, phone, phone_type):
    """Вызов процедуры add_phone (3.4.1)"""
    conn = get_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("CALL add_phone(%s, %s, %s);", (contact_name, phone, phone_type))
            conn.commit()
            print(f"Номер {phone} ({phone_type}) успешно добавлен контакту '{contact_name}'!")
            cursor.close()
        except Exception as error:
            print("Ошибка при добавлении номера:", error)
        finally:
            conn.close()


def move_contact_to_group(contact_name, group_name):
    """Вызов процедуры move_to_group (3.4.2)"""
    conn = get_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("CALL move_to_group(%s, %s);", (contact_name, group_name))
            conn.commit()
            print(f"Контакт '{contact_name}' перемещен в группу '{group_name}'!")
            cursor.close()
        except Exception as error:
            print("Ошибка при перемещении в группу:", error)
        finally:
            conn.close()


def filter_and_sort_contacts(group_name=None, email_query=None, sort_by="name"):
    """Фильтрация по группе, поиск по email и сортировка (3.2.1, 3.2.2, 3.2.3)"""
    order_map = {
        "name": "c.first_name ASC, c.last_name ASC",
        "birthday": "c.birthday ASC NULLS LAST",
        "date": "c.created_at DESC"
    }
    order_clause = order_map.get(sort_by, "c.id ASC")

    sql = f"""
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
    WHERE (%s IS NULL OR g.name ILIKE %s)
      AND (%s IS NULL OR c.email ILIKE '%%' || %s || '%%')
    GROUP BY c.id, g.name
    ORDER BY {order_clause};
    """
    conn = get_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (group_name, group_name, email_query, email_query))
            rows = cursor.fetchall()
            title = f"Фильтр (Группа: {group_name or 'Все'}, Email: {email_query or 'Все'}, Сортировка: {sort_by})"
            print_contacts_table(rows, title)
            cursor.close()
        except Exception as error:
            print("Ошибка при фильтрации/сортировке:", error)
        finally:
            conn.close()


def paginate_contacts_loop(page_size=5):
    """Интерактивная навигация по страницам next / prev / quit (3.2.4)"""
    offset = 0
    while True:
        conn = get_connection()
        rows = []
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM get_contacts_paginated(%s, %s);", (page_size, offset))
                rows = cursor.fetchall()
                cursor.close()
            except Exception as error:
                print("Ошибка пагинации:", error)
                break
            finally:
                conn.close()

        page_num = (offset // page_size) + 1
        print_contacts_table(rows, f"Страница {page_num} (Показано с {offset + 1}, лимит {page_size})")

        cmd = input("Навигация: [n]ext (след.) / [p]rev (пред.) / [q]uit (выход): ").strip().lower()
        if cmd in ('n', 'next'):
            if len(rows) < page_size:
                print("Это последняя страница!")
            else:
                offset += page_size
        elif cmd in ('p', 'prev'):
            if offset == 0:
                print("Вы уже на первой странице!")
            else:
                offset = max(0, offset - page_size)
        elif cmd in ('q', 'quit'):
            break
        else:
            print("Неверная команда. Введите next, prev или quit.")

def update_contact(old_phone, new_first_name, new_phone):
    sql_update = """
    UPDATE contacts
    SET first_name = %s, phone = %s
    WHERE phone = %s;
    """
    conn = get_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute(sql_update, (new_first_name, new_phone, old_phone))
            conn.commit()
            
            if cursor.rowcount > 0:
                print(f"Контакт с номером {old_phone} успешно обновлен!")
            else:
                print(f"Контакт с номером {old_phone} не найден.")
                
            cursor.close()
        except Exception as error:
            print("Ошибка при обновлении:", error)
        finally:
            conn.close()

def delete_contact(identifier):
    sql_call = "CALL delete_contact_proc(%s);"
    conn = get_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute(sql_call, (identifier,))
            conn.commit()
            print(f"Команда на удаление '{identifier}' отправлена в базу.")
            cursor.close()
        except Exception as error:
            print("Ошибка при удалении:", error)
        finally:
            conn.close()

def query_contacts_paginated(limit, offset):
    sql_call = "SELECT * FROM get_contacts_paginated(%s, %s);"
    conn = get_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute(sql_call, (limit, offset))
            rows = cursor.fetchall()
            
            print(f"\n--- Страница контактов (Лимит: {limit}, Пропущено: {offset}) ---")
            if not rows:
                print("На этой странице пусто.")
            else:
                print(f"{'ID':<5} | {'Имя и Фамилия':<25} | {'Телефон':<17}")
                print("-" * 53)
                for row in rows:
                    full_name = f"{row[1]} {row[2] or ''}".strip()
                    print(f"{row[0]:<5} | {full_name:<25} | {row[3]:<17}")
            print("-" * 53 + "\n")
            cursor.close()
        except Exception as error:
            print("Ошибка при получении страницы:", error)
        finally:
            conn.close()

def insert_contact_extended(first_name, last_name, phone, phone_type='mobile', email=None, birthday=None, group_name=None):
    """Добавление контакта со всеми расширенными полями"""
    sql_call = "CALL upsert_contact(%s, %s, %s);"
    conn = get_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute(sql_call, (first_name, last_name, phone))
            
            # Обновляем email и birthday, если они переданы
            cursor.execute("""
                UPDATE contacts 
                SET email = COALESCE(%s, email), 
                    birthday = COALESCE(%s::DATE, birthday)
                WHERE first_name = %s;
            """, (email if email else None, birthday if birthday else None, first_name))

            # Устанавливаем тип телефона
            if phone_type in ('home', 'work', 'mobile'):
                cursor.execute("CALL add_phone(%s, %s, %s);", (first_name, phone, phone_type))

            # Если указана группа, привязываем через процедуру move_to_group
            if group_name:
                cursor.execute("CALL move_to_group(%s, %s);", (first_name, group_name))

            conn.commit()
            cursor.close()
            print(f"Контакт {first_name} успешно сохранен!")
        except Exception as error:
            print("Ошибка при сохранении контакта:", error)
        finally:
            conn.close()

def main_menu():
    """Главное интерактивное меню приложения TSIS 1"""
    while True:
        print("\n========= ТЕЛЕФОННАЯ КНИГА (TSIS 1) =========")
        print("1. Добавить/обновить контакт (со всеми полями)")
        print("2. Добавить дополнительный номер контакту (add_phone)")
        print("3. Переместить контакт в группу (move_to_group)")
        print("4. Глобальный поиск (search_contacts: имя, email, все номера)")
        print("5. Фильтр по группе / Поиск по Email / Сортировка")
        print("6. Навигация по страницам (Пагинация: next / prev / quit)")
        print("7. Загрузить контакты из CSV (расширенный)")
        print("8. Экспорт контактов в JSON")
        print("9. Импорт контактов из JSON (skip / overwrite)")
        print("10. Изменить имя контакта (по старому номеру)")
        print("11. Удалить контакт")
        print("0. Выйти")
        print("=============================================")
        
        choice = input("Выберите действие (0-11): ").strip()
        
        if choice == '1':
            print("\n-- Добавление / обновление контакта --")
            first_name = input("Имя (обязательно): ").strip()
            if not first_name:
                print("Имя не может быть пустым!")
                continue
            last_name = input("Фамилия (Enter чтобы пропустить): ").strip()
            phone = input("Номер телефона (например +77011234567): ").strip()
            if not phone:
                print("Номер телефона не может быть пустым!")
                continue
            phone_type = input("Тип телефона (mobile/home/work, по умолчанию mobile): ").strip().lower() or 'mobile'
            email = input("Email (Enter чтобы пропустить): ").strip() or None
            birthday = input("Дата рождения ГГГГ-ММ-ДД (Enter чтобы пропустить): ").strip() or None
            group_name = input("Группа (Family/Work/Friend/Other, Enter чтобы пропустить): ").strip() or None
            
            insert_contact_extended(first_name, last_name, phone, phone_type, email, birthday, group_name)
            
        elif choice == '2':
            print("\n-- Добавление второго/нового номера (add_phone) --")
            name = input("Введите имя контакта: ").strip()
            phone = input("Введите дополнительный номер: ").strip()
            p_type = input("Тип номера (mobile / home / work): ").strip().lower() or 'mobile'
            if name and phone:
                add_extra_phone(name, phone, p_type)
            else:
                print("Имя и номер обязательны!")

        elif choice == '3':
            print("\n-- Перемещение в группу (move_to_group) --")
            name = input("Введите имя контакта: ").strip()
            group = input("Введите название группы (например Family, Work, Friend, VIP): ").strip()
            if name and group:
                move_contact_to_group(name, group)
            else:
                print("Имя и группа обязательны!")

        elif choice == '4':
            print("\n-- Глобальный поиск --")
            search_term = input("Введите запрос (имя, email или телефон, Enter = все): ").strip()
            query_contacts(search_term)

        elif choice == '5':
            print("\n-- Фильтр, поиск по Email и сортировка --")
            grp = input("Фильтр по группе (Family/Work/Friend/Other или Enter = все): ").strip() or None
            eml = input("Поиск по части Email (например gmail или Enter = все): ").strip() or None
            srt = input("Сортировать по [name / birthday / date] (по умолчанию name): ").strip().lower() or "name"
            filter_and_sort_contacts(grp, eml, srt)

        elif choice == '6':
            print("\n-- Постраничная навигация --")
            try:
                sz = input("Размер страницы (по умолчанию 5): ").strip()
                page_size = int(sz) if sz else 5
                paginate_contacts_loop(page_size)
            except ValueError:
                print("Ошибка: нужно ввести число!")

        elif choice == '7':
            print("\n-- Загрузка из CSV --")
            filename = input("Имя файла (по умолчанию contacts.csv): ").strip() or 'contacts.csv'
            insert_from_csv(filename)

        elif choice == '8':
            print("\n-- Экспорт в JSON --")
            filename = input("Имя файла (по умолчанию contacts.json): ").strip() or 'contacts.json'
            export_to_json(filename)

        elif choice == '9':
            print("\n-- Импорт из JSON --")
            filename = input("Имя файла (по умолчанию contacts.json): ").strip() or 'contacts.json'
            import_from_json(filename)

        elif choice == '10':
            print("\n-- Обновление контакта --")
            old_phone = input("Введите ТЕКУЩИЙ номер телефона контакта: ").strip()
            new_name = input("Введите НОВОЕ имя: ").strip()
            new_phone = input("Введите НОВЫЙ номер телефона: ").strip()
            if old_phone and new_name and new_phone:
                update_contact(old_phone, new_name, new_phone)
            else:
                print("Ошибка: Все поля должны быть заполнены!")

        elif choice == '11':
            print("\n-- Удаление контакта --")
            identifier = input("Введите Имя или Номер телефона для удаления: ").strip()
            if identifier:
                delete_contact(identifier)
            else:
                print("Ошибка: Вы ничего не ввели!")

        elif choice == '0':
            print("\nВыход из программы. До свидания!")
            break
        else:
            print("\nНеверный ввод. Пожалуйста, выберите число от 0 до 11.")

if __name__ == '__main__':
    create_table()
    create_db_functions()
    main_menu()
