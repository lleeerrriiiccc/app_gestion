# Database Structure: suimco

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

## Tabla: facturas
| Columna | Tipo | Nulo | Clave | Valor por defecto | Extra |
|----------|------|------|-------|------------------|--------|
| cliente | int(11) | YES | MUL | None |  |
| ubicacion_factura | text | YES |  | None |  |
| factura_pendiente | int(11) | YES |  | None |  |
| email | text | YES |  | None |  |
| idfactura | int(11) | NO | MUL | None | auto_increment |

### Relaciones:
- cliente → clientes.idcliente

## Tabla: users
| Columna | Tipo | Nulo | Clave | Valor por defecto | Extra |
|----------|------|------|-------|------------------|--------|
| id | int(11) | NO | PRI | None | auto_increment |
| user | text | YES |  | None |  |
| pass | text | YES |  | None |  |
| privilege | int(11) | YES |  | None |  |

