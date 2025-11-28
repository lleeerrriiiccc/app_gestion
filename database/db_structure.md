# Database Structure: suimco

## Tabla: assignaciones
| Columna | Tipo | Nulo | Clave | Valor por defecto | Extra |
|----------|------|------|-------|------------------|--------|
| pedido | int(11) | YES | MUL | None |  |
| empleado | int(11) | YES | MUL | None |  |
| proceso | int(11) | YES | MUL | None |  |
| maquina | int(11) | YES | MUL | None |  |
| idlinia | int(11) | YES | MUL | None |  |
| estado | int(11) | YES |  | 0 |  |
| fecha_entrada | date | YES |  | None |  |
| fecha_salida | date | YES |  | None |  |

### Relaciones:
- empleado → users.id
- idlinia → linias_pedido.idlinia
- maquina → maquinas.idmaquina
- pedido → pedidos.idpedido
- proceso → procesos.idproceso

## Tabla: clientes
| Columna | Tipo | Nulo | Clave | Valor por defecto | Extra |
|----------|------|------|-------|------------------|--------|
| name | text | YES |  | None |  |
| idcliente | int(11) | NO | MUL | None | auto_increment |
| nif | int(11) | YES |  | None |  |

## Tabla: datos_contacto
| Columna | Tipo | Nulo | Clave | Valor por defecto | Extra |
|----------|------|------|-------|------------------|--------|
| cliente | int(11) | NO | PRI | None |  |
| idcontacto | int(11) | NO | PRI | None |  |
| name | text | YES |  | None |  |
| email | text | YES |  | None |  |
| tel | int(11) | YES |  | None |  |
| facturas | int(11) | YES |  | None |  |

### Relaciones:
- cliente → clientes.idcliente

## Tabla: datos_envio
| Columna | Tipo | Nulo | Clave | Valor por defecto | Extra |
|----------|------|------|-------|------------------|--------|
| cliente | int(11) | NO | PRI | None |  |
| idregistro | int(11) | NO | PRI | None |  |
| poblacion | text | YES |  | None |  |
| codigo_postal | int(11) | YES |  | None |  |
| direccion | text | YES |  | None |  |
| pais | text | YES |  | None |  |

### Relaciones:
- cliente → clientes.idcliente

## Tabla: departamentos
| Columna | Tipo | Nulo | Clave | Valor por defecto | Extra |
|----------|------|------|-------|------------------|--------|
| iddept | int(11) | NO | PRI | None | auto_increment |
| name | text | NO |  | None |  |
| menu | text | NO |  | '{}' |  |

## Tabla: despiece_productos
| Columna | Tipo | Nulo | Clave | Valor por defecto | Extra |
|----------|------|------|-------|------------------|--------|
| producto | int(11) | NO | PRI | None |  |
| pieza | int(11) | NO | PRI | None |  |

### Relaciones:
- pieza → piezas.idpiezas
- producto → producto.idproducto

## Tabla: facturas
| Columna | Tipo | Nulo | Clave | Valor por defecto | Extra |
|----------|------|------|-------|------------------|--------|
| cliente | int(11) | YES | MUL | None |  |
| ubicacion_factura | text | YES |  | None |  |
| factura_pendiente | int(11) | YES |  | None |  |
| email | text | YES |  | None |  |
| idfactura | int(11) | NO | PRI | None | auto_increment |
| pedido | int(11) | YES | MUL | None |  |
| fecha | date | YES |  | None |  |

### Relaciones:
- cliente → clientes.idcliente
- pedido → pedidos.idpedido

## Tabla: linias_pedido
| Columna | Tipo | Nulo | Clave | Valor por defecto | Extra |
|----------|------|------|-------|------------------|--------|
| idlinia | int(11) | NO | PRI | None | auto_increment |
| pedido | int(11) | NO | MUL | None |  |
| producto | int(11) | YES | MUL | None |  |
| cantidad | int(11) | YES |  | None |  |

### Relaciones:
- pedido → pedidos.idpedido
- producto → producto.idproducto

## Tabla: maquinas
| Columna | Tipo | Nulo | Clave | Valor por defecto | Extra |
|----------|------|------|-------|------------------|--------|
| idmaquina | int(11) | NO | PRI | None | auto_increment |
| nombre | text | YES |  | None |  |
| proceso | int(11) | YES | MUL | None |  |

### Relaciones:
- proceso → procesos.idproceso

## Tabla: notificaciones
| Columna | Tipo | Nulo | Clave | Valor por defecto | Extra |
|----------|------|------|-------|------------------|--------|
| id | int(11) | NO | PRI | None | auto_increment |
| usuario_destino | varchar(255) | YES |  | None |  |
| remitente | varchar(255) | YES |  | None |  |
| mensaje | text | YES |  | None |  |
| metadata | longtext | YES |  | None |  |
| leido | tinyint(1) | YES |  | 0 |  |
| fecha | datetime | YES |  | current_timestamp() |  |

## Tabla: pedidos
| Columna | Tipo | Nulo | Clave | Valor por defecto | Extra |
|----------|------|------|-------|------------------|--------|
| idpedido | int(11) | NO | PRI | None | auto_increment |
| cliente | int(11) | NO | MUL | 0 |  |
| direccion_envio | int(11) | NO |  | 0 |  |
| fecha_taller | date | YES |  | None |  |
| estado | int(11) | YES |  | 0 |  |
| assignado | int(11) | YES |  | 0 |  |
| fecha_completado | date | YES |  | None |  |

### Relaciones:
- cliente → clientes.idcliente
- cliente → datos_envio.cliente
- direccion_envio → datos_envio.idregistro

## Tabla: piezas
| Columna | Tipo | Nulo | Clave | Valor por defecto | Extra |
|----------|------|------|-------|------------------|--------|
| idpiezas | int(11) | NO | PRI | None | auto_increment |
| name | text | YES |  | None |  |
| codigo | text | YES |  | None |  |
| plano | text | YES |  | 'No hay planos para este producto' |  |

## Tabla: procesos
| Columna | Tipo | Nulo | Clave | Valor por defecto | Extra |
|----------|------|------|-------|------------------|--------|
| idproceso | int(11) | NO | PRI | None | auto_increment |
| descripcion | text | YES |  | None |  |

## Tabla: producto
| Columna | Tipo | Nulo | Clave | Valor por defecto | Extra |
|----------|------|------|-------|------------------|--------|
| idproducto | int(11) | NO | PRI | None | auto_increment |
| material | int(11) | YES |  | 0 |  |
| descripcion | text | YES |  | None |  |
| nombre | text | YES |  | None |  |
| codigo | text | YES |  | None |  |
| precio | int(11) | YES |  | None |  |
| planos | text | YES |  | 'No hay planos para este producto' |  |

## Tabla: users
| Columna | Tipo | Nulo | Clave | Valor por defecto | Extra |
|----------|------|------|-------|------------------|--------|
| id | int(11) | NO | PRI | None | auto_increment |
| user | text | YES |  | None |  |
| pass | text | YES |  | None |  |
| privilege | int(11) | YES |  | None |  |
| dept | int(11) | YES | MUL | None |  |

### Relaciones:
- dept → departamentos.iddept

