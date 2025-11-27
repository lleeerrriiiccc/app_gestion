import database as db
def send_notification(payload, sender='system',socketio=None):
    """
    Envía una notificación usando los objetos db y socketio proporcionados.

    payload: dict con keys 'to', 'message', opcional 'persist'
    sender: nombre del remitente (str)
    db: objeto con método add_notification(usuario, sender, message, metadata, persist)
    socketio: objeto con método emit(event, payload, room=None)

    Devuelve (mensaje_str, status_code)
    """

    to = payload.get('to')
    message = payload.get('mensaje')
    persist = payload.get('persist', True)
    try:

        if not to or to in ('all', 'broadcast'):
            db.add_notification(None, sender, message, metadata=None, persist=persist)
            socketio.emit('notificacion', {'usuario': sender, 'mensaje': message})
        elif isinstance(to, list):
            for u in to:
                db.add_notification(u, sender, message, metadata=None, persist=persist)
                socketio.emit('notificacion', {'usuario': sender, 'mensaje': message}, room=str(u))
        else:
            db.add_notification(to, sender, message, metadata=None, persist=persist)
            socketio.emit('notificacion', {'usuario': sender, 'mensaje': message}, room=str(to))

        return ('Notification sent', 201)
    except Exception as e:
        print('send_notification error:', e)
        return (f'Error: {e}', 500)