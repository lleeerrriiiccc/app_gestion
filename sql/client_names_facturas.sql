SELECT 
facturas.idfactura,
clientes.name
FROM facturas
INNER JOIN clientes
	ON facturas.cliente = clientes.idcliente;