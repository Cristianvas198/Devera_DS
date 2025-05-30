DROP TABLE IF EXISTS brand CASCADE;
DROP TABLE IF EXISTS url CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS products_materials CASCADE;
DROP TABLE IF EXISTS products_processes CASCADE;
DROP TABLE IF EXISTS products_impacts CASCADE;
DROP TABLE IF EXISTS products_impacts_resume CASCADE;

CREATE TABLE brand (
  id_brand serial NOT NULL PRIMARY KEY, 
  name_brand varchar(25) NOT NULL
);

CREATE TABLE url (
  id_url serial NOT NULL PRIMARY KEY, 
  name_url varchar(150) NOT NULL,
  date_created timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  id_brand int NOT NULL,
  FOREIGN KEY (id_brand) REFERENCES brand(id_brand)
);

CREATE TABLE products (
  id_products serial NOT NULL PRIMARY KEY, 
  product_name varchar(150) NOT NULL,
  href varchar(150) NOT NULL,
  product_flag boolean NOT NULL DEFAULT false,
  packaging varchar(150),
  total_weight float(24),
  transporting_distance float(24),
  id_brand int NOT NULL,
  FOREIGN KEY (id_brand) REFERENCES brand(id_brand)
);

CREATE TABLE products_materials (
  id_products_materials serial NOT NULL PRIMARY KEY, 
  id_products int NOT NULL,
  name_material varchar(50) NOT NULL,
  quantity float(24),
  quantity_of_recycling float(24),
  FOREIGN KEY (id_products) REFERENCES products(id_products)
);

CREATE TABLE products_processes (
  id_products_processes serial NOT NULL PRIMARY KEY, 
  id_products int NOT NULL,
  name_process varchar(50) NOT NULL,
  quantity_of_consumption float(24),
  country varchar(50),
  FOREIGN KEY (id_products) REFERENCES products(id_products)
);

CREATE TABLE products_impacts (
  id_products_impacts serial NOT NULL PRIMARY KEY, 
  id_products int NOT NULL,
  raw_materials float(24),
  manufacturing float(24),
  transport float(24),
  packaging float(24),
  product_use float(24) DEFAULT 0,
  end_of_life float(24) DEFAULT 0,
  FOREIGN KEY (id_products) REFERENCES products(id_products)
);

CREATE TABLE products_impacts_resume (
  id_pir serial NOT NULL PRIMARY KEY, 
  id_products int NOT NULL,
  co2_firgerprint float(24),
  pct_benchmark float(24),
  impact_score int,
  seal varchar(5),
  status varchar(25),
  FOREIGN KEY (id_products) REFERENCES products(id_products)
);

ALTER TABLE users 
ADD COLUMN id_brand int;

ALTER TABLE users
ADD CONSTRAINT fk_users_brand
FOREIGN KEY (id_brand)
REFERENCES brand(id_brand);








INSERT INTO brand(name_brand)
VALUES
('SAIGU');

INSERT INTO products(id_brand,product_name,href)
VALUES
(1,'Labial rojo','https://saigucosmetics.com/collections/all-products/products/pintalabios-melting-glow'),
(1,'Mascara de pestañas','https://saigucosmetics.com/products/mascara-de-pestanas'),
(1,'Base de maquillaje','https://saigucosmetics.com/products/base-de-maquillaje-fluida');

INSERT INTO products_impacts_resume(id_products, co2_firgerprint, pct_benchmark, impact_score, seal, status)
VALUES
(1,0.30,-15,65,'E','Pending'),
(2,0.25,-37,85,'A','Finalized'),
(3,0.15,-20,70,'C','Processing');

UPDATE users
SET id_brand = 1;


