// Conexión global a Socket.IO
const socket = io({
    transports: ["websocket", "polling"]
});
// Escuchar notificaciones del servidor
socket.on('notificacion', function(data) {
    recibirNotificacion(data.usuario, data.mensaje);
});

// Función reutilizable para manejar la notificación
function recibirNotificacion(usuario, mensaje) {
    // ¡Cámbialo si quieres filtrar por usuario!
    console.log("Notificación:", mensaje);

    // Ejemplo básico:
    alert("Notificación: " + mensaje);

    // Si quieres usar SweetAlert o Toastr, aquí sería el sitio.
}
