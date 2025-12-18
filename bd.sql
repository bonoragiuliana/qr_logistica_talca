CREATE DATABASE productos_db;

USE productos_db;

CREATE TABLE productos (
    id_producto INT PRIMARY KEY,
    descripcion VARCHAR(255),
    ultimo_nro_serie INT DEFAULT 0
);

INSERT INTO productos VALUES
(417, 'SODA ½ LITRO * 12 PET Pack TALCA', 0),
(4900, 'SODA TALCA 2¼ LITRO PET* 6 U. Pack TALCA', 0),
(5051, 'TALCA COLA PET ½L DESC *12U Pack TALCA', 0),
(5056, 'TALCA LIMA LIMON PT½L DESC*12U Pack TALCA', 0);





