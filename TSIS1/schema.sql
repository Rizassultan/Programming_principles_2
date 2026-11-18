-- 1. Базовая таблица контактов (если запускается с нуля)
CREATE TABLE IF NOT EXISTS contacts (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50),
    phone VARCHAR(20) UNIQUE
);

-- Делаем старую колонку phone необязательной, так как теперь телефоны в таблице phones
ALTER TABLE contacts ALTER COLUMN phone DROP NOT NULL;

-- 2. Таблица групп (Family, Work, Friend, Other)
CREATE TABLE IF NOT EXISTS groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- Заполняем стандартными группами из задания
INSERT INTO groups (name) VALUES ('Family'), ('Work'), ('Friend'), ('Other')
ON CONFLICT (name) DO NOTHING;

-- 3. Расширяем таблицу contacts новыми полями (и датой добавления для сортировки)
ALTER TABLE contacts
    ADD COLUMN IF NOT EXISTS email VARCHAR(100),
    ADD COLUMN IF NOT EXISTS birthday DATE,
    ADD COLUMN IF NOT EXISTS group_id INTEGER REFERENCES groups(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- 4. Таблица телефонов (1-ко-многим)
CREATE TABLE IF NOT EXISTS phones (
    id SERIAL PRIMARY KEY,
    contact_id INTEGER REFERENCES contacts(id) ON DELETE CASCADE,
    phone VARCHAR(20) NOT NULL,
    type VARCHAR(10) CHECK (type IN ('home', 'work', 'mobile')),
    UNIQUE(contact_id, phone)
);

-- Переносим уже существующие номера из contacts.phone в таблицу phones (как 'mobile'), если они еще не там
INSERT INTO phones (contact_id, phone, type)
SELECT id, phone, 'mobile' FROM contacts WHERE phone IS NOT NULL
ON CONFLICT (contact_id, phone) DO NOTHING;