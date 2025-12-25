

-- Таблица комнат
CREATE TABLE IF NOT EXISTS rooms (
    id SERIAL PRIMARY KEY,
    uuid VARCHAR(36) UNIQUE DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    agora_channel_name VARCHAR(255) UNIQUE NOT NULL,
    is_private BOOLEAN DEFAULT FALSE,
    max_participants INTEGER DEFAULT 50,
    created_by VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Таблица логов токенов
CREATE TABLE IF NOT EXISTS tokens_log (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    channel VARCHAR(255),
    token_type VARCHAR(10) NOT NULL CHECK (token_type IN ('rtc', 'rtm')),
    token_hash VARCHAR(64) NOT NULL,
    issued_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для производительности
CREATE INDEX IF NOT EXISTS idx_rooms_uuid ON rooms(uuid);
CREATE INDEX IF NOT EXISTS idx_rooms_created_by ON rooms(created_by);
CREATE INDEX IF NOT EXISTS idx_rooms_created_at ON rooms(created_at);
CREATE INDEX IF NOT EXISTS idx_tokens_log_user_id ON tokens_log(user_id);
CREATE INDEX IF NOT EXISTS idx_tokens_log_token_type ON tokens_log(token_type);
CREATE INDEX IF NOT EXISTS idx_tokens_log_issued_at ON tokens_log(issued_at);
CREATE INDEX IF NOT EXISTS idx_tokens_log_expires_at ON tokens_log(expires_at);

-- Триггер для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE OR REPLACE TRIGGER update_rooms_updated_at
    BEFORE UPDATE ON rooms
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Комментарии к таблицам
COMMENT ON TABLE rooms IS 'Таблица комнат для видео-стримов';
COMMENT ON TABLE tokens_log IS 'Логи выданных токенов Agora';