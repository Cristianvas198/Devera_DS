DROP TABLE IF EXISTS brand CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS products_materials CASCADE;
DROP TABLE IF EXISTS products_processes CASCADE;
DROP TABLE IF EXISTS products_impacts CASCADE;
DROP TABLE IF EXISTS products_impacts_resume CASCADE;

CREATE TABLE brand (
  id_brand serial NOT NULL PRIMARY KEY, 
  name_brand varchar(25) NOT NULL
);



CREATE TABLE products (
  id_products serial NOT NULL PRIMARY KEY, 
  product_name varchar(150) NOT NULL,
  href varchar(150) NOT NULL,
  total_weight float(24),
  transporting_distance float(24),
  pct_recycling float(24),
  id_brand int NOT NULL,
  transporting_type varchar(150),
  product_folder varchar(1000)
  FOREIGN KEY (id_brand) REFERENCES brand(id_brand)
);

CREATE TABLE products_materials (
  id_products_materials serial NOT NULL PRIMARY KEY, 
  id_products int NOT NULL,
  name_material varchar(50) NOT NULL,
  quantity float(24),
  pct_recycling float(24),
  pct_product float(24),
  country varchar(50),
  co2_impact float(24),
  FOREIGN KEY (id_products) REFERENCES products(id_products)
);

CREATE TABLE products_processes (
  id_products_processes serial NOT NULL PRIMARY KEY, 
  id_products int NOT NULL,
  name_process varchar(50) NOT NULL,
  quantity_energy float(24),
  country varchar(50),
  type_consumption varchar(50),
  quantity_water float(24),
  co2_impact float(24),
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
  product_pdf varchar(1000)
  FOREIGN KEY (id_products) REFERENCES products(id_products)
);

CREATE TABLE users
(
    id integer NOT NULL DEFAULT PRIMARY KEY,
    name text NOT NULL,
    email text NOT NULL,
    password text NOT NULL,
    logged boolean DEFAULT false,
    image_url text,
    id_brand integer,
    FOREIGN KEY (id_brand)REFERENCES brand (id_brand) )


CREATE TABLE products_impacts_resume
(
    id_pir integer NOT NULL PRIMARY KEY,
    id_products integer NOT NULL,
    co2_firgerprint real,
    pct_benchmark real,
    impact_score integer,
    seal varying(5),
    status varying(25),
    FOREIGN KEY (id_products) REFERENCES products (id_products));


CREATE TABLE products_packing (
  id_products_packing serial NOT NULL PRIMARY KEY, 
  id_products int NOT NULL,
  packing_name varchar(150),
  packing_weight float(24),
  packing_material varchar(150),
  pct_recycling float(24),
  country varchar(150),
  type_use varchar(150),
  FOREIGN KEY (id_products) REFERENCES products(id_products));

CREATE TABLE form
(
    id_form integer NOT NULL PRIMARY KEY,
    id_brand integer NOT NULL,
    company_name text NOT NULL,
    employees integer NOT NULL,
    sustainability_report boolean NOT NULL,
    percent_renewable_sources text NOT NULL,
    plan_carbon_footprint text NOT NULL,
    percent_virgin_material text NOT NULL,
    distance_providers text NOT NULL,
    news_sustainability text  NOT NULL,
    equality_plan text  NOT NULL,
    wage_gap text  NOT NULL,
    conciliation_measures text NOT NULL,
    enps_measurement text NOT NULL,
    proyectossociales text,
    otrainfo text,
    certificados text,
    FOREIGN KEY (id_brand) REFERENCES brand (id_brand));


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


