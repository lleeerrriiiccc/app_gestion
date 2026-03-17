CREATE TABLE IF NOT EXISTS "assignaciones" (
  "pedido" INTEGER DEFAULT NULL,
  "empleado" INTEGER DEFAULT NULL,
  "proceso" INTEGER DEFAULT NULL,
  "maquina" INTEGER DEFAULT NULL,
  "idlinia" INTEGER DEFAULT NULL,
  "estado" INTEGER DEFAULT 0,
  "fecha_entrada" date DEFAULT NULL,
  "fecha_salida" date DEFAULT NULL,
  KEY "pedidoid" ("pedido"),
  KEY "empleadoid" ("empleado"),
  KEY "procesoid" ("proceso"),
  KEY "maquinaid" ("maquina"),
  KEY "fk_assign_lin" ("idlinia"),
  CONSTRAINT "empleadoid" FOREIGN KEY ("empleado") REFERENCES "users" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT "fk_assign_lin" FOREIGN KEY ("idlinia") REFERENCES "linias_pedido" ("idlinia") ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT "maquinaid" FOREIGN KEY ("maquina") REFERENCES "maquinas" ("idmaquina") ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT "pedidoid" FOREIGN KEY ("pedido") REFERENCES "pedidos" ("idpedido") ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT "procesoid" FOREIGN KEY ("proceso") REFERENCES "procesos" ("idproceso") ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla suimco.assignaciones: ~20 rows (aproximadamente)
INSERT INTO "assignaciones" ("pedido", "empleado", "proceso", "maquina", "idlinia", "estado", "fecha_entrada", "fecha_salida") VALUES
	(80, 22, 1, 1, 84, 2, '2025-11-27', NULL),
	(80, 20, 2, NULL, 84, 0, '2025-11-27', NULL),
	(80, 22, 3, NULL, 84, 0, '2025-11-27', NULL),
	(80, NULL, 4, NULL, 84, 2, '2025-11-27', NULL),
	(80, NULL, 5, NULL, 84, 2, '2025-11-27', NULL),
	(81, 22, 1, 1, 85, 2, '2025-12-01', NULL),
	(81, NULL, 2, NULL, 85, 2, '2025-12-01', NULL),
	(81, NULL, 3, NULL, 85, 2, '2025-12-01', NULL),
	(81, NULL, 4, NULL, 85, 2, '2025-12-01', NULL),
	(81, NULL, 5, NULL, 85, 2, '2025-12-01', NULL),
	(82, 20, 1, NULL, 86, 0, '2025-12-10', NULL),
	(82, 20, 2, NULL, 86, 0, '2025-12-10', NULL),
	(82, 20, 3, NULL, 86, 0, '2025-12-10', NULL),
	(82, 20, 4, NULL, 86, 0, '2025-12-10', NULL),
	(82, 20, 5, NULL, 86, 0, '2025-12-10', NULL),
	(82, 20, 1, NULL, 87, 0, '2025-12-10', NULL),
	(82, 20, 2, NULL, 87, 0, '2025-12-10', NULL),
	(82, 20, 3, NULL, 87, 0, '2025-12-10', NULL),
	(82, 20, 4, NULL, 87, 0, '2025-12-10', NULL),
	(82, 20, 5, NULL, 87, 0, '2025-12-10', NULL);

-- Volcando estructura para tabla suimco.chapas
CREATE TABLE IF NOT EXISTS "chapas" (
  "id" INTEGER NOT NULL AUTO_INCREMENT,
  "tipo" INTEGER DEFAULT NULL,
  PRIMARY KEY ("id"),
  KEY "tipo_fk" ("tipo"),
  CONSTRAINT "tipo_fk" FOREIGN KEY ("tipo") REFERENCES "tipos_chapa" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION
) AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla suimco.chapas: ~0 rows (aproximadamente)
INSERT INTO "chapas" ("id", "tipo") VALUES
	(1, 2);

-- Volcando estructura para tabla suimco.chapa_piezas
CREATE TABLE IF NOT EXISTS "chapa_piezas" (
  "idchapa" INTEGER DEFAULT NULL,
  "idpieza" INTEGER DEFAULT NULL,
  "idpedido" INTEGER DEFAULT NULL,
  KEY "chapa_fk" ("idchapa"),
  KEY "pieza_fk" ("idpieza"),
  KEY "pedido_fk" ("idpedido"),
  CONSTRAINT "chapa_fk" FOREIGN KEY ("idchapa") REFERENCES "chapas" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT "pedido_fk" FOREIGN KEY ("idpedido") REFERENCES "pedidos" ("idpedido") ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT "pieza_fk" FOREIGN KEY ("idpieza") REFERENCES "piezas" ("idpiezas") ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla suimco.chapa_piezas: ~0 rows (aproximadamente)
INSERT INTO "chapa_piezas" ("idchapa", "idpieza", "idpedido") VALUES
	(1, 1, 80);



-- Volcando estructura para tabla suimco.despiece_productos
CREATE TABLE IF NOT EXISTS "despiece_productos" (
  "producto" INTEGER NOT NULL,
  "pieza" INTEGER NOT NULL,
  PRIMARY KEY ("producto","pieza"),
  KEY "pieza" ("pieza"),
  CONSTRAINT "pieza" FOREIGN KEY ("pieza") REFERENCES "piezas" ("idpiezas") ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT "producto" FOREIGN KEY ("producto") REFERENCES "producto" ("idproducto") ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla suimco.despiece_productos: ~4 rows (aproximadamente)
INSERT INTO "despiece_productos" ("producto", "pieza") VALUES
	(1, 1),
	(1, 2),
	(3, 3),
	(3, 4);

-- Volcando estructura para tabla suimco.facturas
CREATE TABLE IF NOT EXISTS "facturas" (
  "cliente" INTEGER DEFAULT NULL,
  "ubicacion_factura" text DEFAULT NULL,
  "factura_pendiente" INTEGER DEFAULT NULL,
  "email" text DEFAULT NULL,
  "idfactura" INTEGER NOT NULL AUTO_INCREMENT,
  "pedido" INTEGER DEFAULT NULL,
  "fecha" date DEFAULT NULL,
  PRIMARY KEY ("idfactura"),
  KEY "idfactura" ("idfactura"),
  KEY "cliente" ("cliente"),
  KEY "pedido" ("pedido"),
  CONSTRAINT "cliente" FOREIGN KEY ("cliente") REFERENCES "clientes" ("idcliente") ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT "pedido" FOREIGN KEY ("pedido") REFERENCES "pedidos" ("idpedido") ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=68 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla suimco.facturas: ~2 rows (aproximadamente)
INSERT INTO "facturas" ("cliente", "ubicacion_factura", "factura_pendiente", "email", "idfactura", "pedido", "fecha") VALUES
	(1, 'C:\\Users\\el160\\Desktop\\Coding\\app_gestion\\app_gestion\\files\\bills\\cainox_factura_1.pdf', 1, 'mario@cainox.es', 65, 80, '2025-11-27'),
	(1, 'C:\\Users\\el160\\Desktop\\Coding\\app_gestion\\app_gestion\\files\\bills\\cainox_factura_66.pdf', 0, 'eric@gmail.com', 66, 81, '2025-12-01'),
	(1, 'C:\\Users\\el160\\Desktop\\Coding\\app_gestion\\app_gestion\\files\\bills\\cainox_factura_67.pdf', 1, 'mario@cainox.es', 67, 82, '2025-12-10');

-- Volcando estructura para tabla suimco.linias_pedido
CREATE TABLE IF NOT EXISTS "linias_pedido" (
  "idlinia" INTEGER NOT NULL AUTO_INCREMENT,
  "pedido" INTEGER NOT NULL,
  "producto" INTEGER DEFAULT NULL,
  "cantidad" INTEGER DEFAULT NULL,
  PRIMARY KEY ("idlinia"),
  KEY "idproducto" ("producto"),
  KEY "idpedido" ("pedido"),
  CONSTRAINT "idpedido" FOREIGN KEY ("pedido") REFERENCES "pedidos" ("idpedido") ON DELETE CASCADE,
  CONSTRAINT "idproducto" FOREIGN KEY ("producto") REFERENCES "producto" ("idproducto") ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=88 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla suimco.linias_pedido: ~4 rows (aproximadamente)
INSERT INTO "linias_pedido" ("idlinia", "pedido", "producto", "cantidad") VALUES
	(84, 80, 2, 1),
	(85, 81, 3, 50),
	(86, 82, 3, 10),
	(87, 82, 2, 1);

-- Volcando estructura para tabla suimco.maquinas


-- Volcando estructura para tabla suimco.materiales


-- Volcando estructura para tabla suimco.pedidos
CREATE TABLE IF NOT EXISTS "pedidos" (
  "idpedido" INTEGER NOT NULL AUTO_INCREMENT,
  "cliente" INTEGER NOT NULL DEFAULT 0,
  "direccion_envio" INTEGER NOT NULL DEFAULT 0,
  "fecha_taller" date DEFAULT NULL,
  "estado" INTEGER DEFAULT 0,
  "assignado" INTEGER DEFAULT 0,
  "fecha_completado" date DEFAULT NULL,
  PRIMARY KEY ("idpedido"),
  KEY "envio_pedido" ("cliente","direccion_envio"),
  CONSTRAINT "FK_pedidos_clientes" FOREIGN KEY ("cliente") REFERENCES "clientes" ("idcliente") ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT "envio_pedido" FOREIGN KEY ("cliente", "direccion_envio") REFERENCES "datos_envio" ("cliente", "idregistro") ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=83 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla suimco.pedidos: ~2 rows (aproximadamente)
INSERT INTO "pedidos" ("idpedido", "cliente", "direccion_envio", "fecha_taller", "estado", "assignado", "fecha_completado") VALUES
	(80, 1, 1, NULL, 0, 1, NULL),
	(81, 1, 1, NULL, 2, 1, '2025-12-01'),
	(82, 1, 1, NULL, 0, 1, NULL);

-- Volcando estructura para tabla suimco.piezas
CREATE TABLE IF NOT EXISTS "piezas" (
  "idpiezas" INTEGER NOT NULL AUTO_INCREMENT,
  "name" text DEFAULT NULL,
  "codigo" text DEFAULT NULL,
  "plano" text DEFAULT 'No hay planos para este producto',
  PRIMARY KEY ("idpiezas")
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla suimco.piezas: ~4 rows (aproximadamente)
INSERT INTO "piezas" ("idpiezas", "name", "codigo", "plano") VALUES
	(1, 'perfil derecho sumidero 50', 'sui30450drch', NULL),
	(2, 'perfil izquierdo sumidero 50', 'sui30450izq', NULL),
	(3, 'Perfil Derecho', 'sui30430drch', 'pieza_prod3_0_AEA_1_-_Windows_Server_2022.pdf'),
	(4, 'Perfil Izquierdo', 'sui30430izq', 'pieza_prod3_1_AEA_3_-_Comparticio_de_recursos_i_seguretat_en_Windows_Server_2022.pdf');

-- Volcando estructura para tabla suimco.procesos
CREATE TABLE IF NOT EXISTS "procesos" (
  "idproceso" INTEGER NOT NULL AUTO_INCREMENT,
  "descripcion" text DEFAULT NULL,
  PRIMARY KEY ("idproceso")
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla suimco.procesos: ~5 rows (aproximadamente)
INSERT INTO "procesos" ("idproceso", "descripcion") VALUES
	(1, 'cortado'),
	(2, 'plegado'),
	(3, 'soldadura'),
	(4, 'pulido'),
	(5, 'acabados');

-- Volcando estructura para tabla suimco.producto
CREATE TABLE IF NOT EXISTS "producto" (
  "idproducto" INTEGER NOT NULL AUTO_INCREMENT,
  "material" INTEGER DEFAULT 0,
  "descripcion" text DEFAULT NULL,
  "nombre" text DEFAULT NULL,
  "codigo" text DEFAULT NULL,
  "precio" INTEGER DEFAULT NULL,
  "planos" text DEFAULT 'No hay planos para este producto',
  PRIMARY KEY ("idproducto")
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla suimco.producto: ~2 rows (aproximadamente)
INSERT INTO "producto" ("idproducto", "material", "descripcion", "nombre", "codigo", "precio", "planos") VALUES
	(1, 304, 'sumidero 50', 'sumidero', 'sui30450', 50, 'C:\\Users\\el160\\Desktop\\Coding\\app_gestion\\app_gestion\\files\\planos\\sui30450.pdf'),
	(2, 304, 'canal ducha 900', 'cdb 900', 'cdb304900', 80, 'No hay planos para este producto'),
	(3, 0, 'Suislot inox 304 sobreponer altura 30', 'SuiSlot INOX 304  30 Sobreponer', 'suislot3041230xs', 43, 'AEA_7_part1_elp.pdf');

-- Volcando estructura para tabla suimco.tipos_chapa
CREATE TABLE IF NOT EXISTS "tipos_chapa" (
  "id" INTEGER NOT NULL AUTO_INCREMENT,
  "largo" INTEGER NOT NULL DEFAULT 0,
  "ancho" INTEGER NOT NULL DEFAULT 0,
  "grosor" float NOT NULL DEFAULT 0,
  "material" INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY ("id"),
  KEY "material" ("material"),
  CONSTRAINT "material" FOREIGN KEY ("material") REFERENCES "materiales" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla suimco.tipos_chapa: ~1 rows (aproximadamente)
INSERT INTO "tipos_chapa" ("id", "largo", "ancho", "grosor", "material") VALUES
	(2, 1500, 3000, 1.5, 1),
	(4, 1500, 3000, 2, 1);

