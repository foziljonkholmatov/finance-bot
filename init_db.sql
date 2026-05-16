-- Finance Bot v2 — DB sxemasi

CREATE TABLE IF NOT EXISTS users (
    id            BIGINT PRIMARY KEY,
    username      VARCHAR(64),
    full_name     VARCHAR(128),
    phone         VARCHAR(20),
    latitude      DOUBLE PRECISION,
    longitude     DOUBLE PRECISION,
    is_registered BOOLEAN DEFAULT FALSE,
    is_blocked    BOOLEAN DEFAULT FALSE,
    is_admin      BOOLEAN DEFAULT FALSE,
    created_at    TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS categories (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(64) NOT NULL,
    type       VARCHAR(10) NOT NULL CHECK (type IN ('income','expense')),
    is_default BOOLEAN DEFAULT FALSE
);

INSERT INTO categories (name, type, is_default) VALUES
    ('Maosh',          'income',  TRUE),
    ('Freelance',      'income',  TRUE),
    ('Biznes',         'income',  TRUE),
    ('Boshqa daromad', 'income',  TRUE),
    ('Oziq-ovqat',     'expense', TRUE),
    ('Transport',      'expense', TRUE),
    ('Kommunal',       'expense', TRUE),
    ('Kiyim-kechak',   'expense', TRUE),
    ('Sog''liq',       'expense', TRUE),
    ('Ta''lim',        'expense', TRUE),
    ('O''yin-kulgi',   'expense', TRUE),
    ('Boshqa harajat', 'expense', TRUE)
ON CONFLICT DO NOTHING;

CREATE TABLE IF NOT EXISTS transactions (
    id              SERIAL PRIMARY KEY,
    user_id         BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type            VARCHAR(10) NOT NULL CHECK (type IN ('income','expense')),
    amount          BIGINT NOT NULL CHECK (amount > 0),
    currency        VARCHAR(5) NOT NULL DEFAULT 'UZS',
    amount_original DOUBLE PRECISION,
    category_id     INT REFERENCES categories(id),
    note            VARCHAR(255),
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tx_user_date ON transactions (user_id, created_at);
