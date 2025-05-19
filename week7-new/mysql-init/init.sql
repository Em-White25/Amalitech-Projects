CREATE USER IF NOT EXISTS 'root'@'localhost' IDENTIFIED BY 'rootpassword';
ALTER USER 'root'@'localhost' IDENTIFIED BY 'rootpassword';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;