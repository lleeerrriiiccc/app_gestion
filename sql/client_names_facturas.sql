SELECT
	a.pedido,
	a.empleado,
	u.user AS empleado_user,
	proc.descripcion AS proceso,
	a.proceso AS idproceso,
	m.nombre AS maquina,
	a.idlinia,
	a.estado,
	DATE_FORMAT(p.fecha_taller, '%d-%m-%Y') AS fecha_taller,
	c.name AS cliente_name,
	lp.cantidad,
	pr.nombre AS producto_nombre
FROM assignaciones a
	INNER JOIN users u ON a.empleado = u.id
	INNER JOIN pedidos p ON a.pedido = p.idpedido
	INNER JOIN procesos proc ON a.proceso = proc.idproceso
	LEFT JOIN maquinas m ON a.maquina = m.idmaquina
	LEFT JOIN clientes c ON p.cliente = c.idcliente
	LEFT JOIN linias_pedido lp ON a.idlinia = lp.idlinia
	LEFT JOIN producto pr ON lp.producto = pr.idproducto
WHERE u.user = 'azucena'
ORDER BY p.fecha_taller DESC;