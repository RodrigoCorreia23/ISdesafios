CREATE TABLE IF NOT EXISTS mensagens(
    id Int AUTO_INCREMENT PRIMARY KEY,
    texto VARCHAR(255) NOT NULL
);

INSERT INTO mensagens (texto) VALUES ('Bem Vindo ao Docker com Python e MYsql');