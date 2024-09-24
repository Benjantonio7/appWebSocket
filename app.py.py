import asyncio
import websockets
import json

# Diccionario para almacenar conexiones de usuarios por canales
channels = {}

async def handler(websocket, path):
    try:
        # Espera la conexión inicial con los datos del usuario
        async for message in websocket:
            data = json.loads(message)
            action = data.get('action')
            
            if action == 'join':
                # Si el usuario quiere unirse a un canal
                username = data.get('username')
                channel_name = data.get('channel')
                
                if channel_name not in channels:
                    channels[channel_name] = set()
                
                channels[channel_name].add(websocket)
                await notify_channel(channel_name, f"{username} se ha unido al canal {channel_name}.")
            
            elif action == 'message':
                # Mensaje para el canal
                channel_name = data.get('channel')
                username = data.get('username')
                msg = data.get('message')
                
                if channel_name in channels:
                    await notify_channel(channel_name, f"{username}: {msg}")
                    
    except websockets.ConnectionClosed:
        # Manejar desconexión
        print("Conexión cerrada")
    finally:
        # Eliminar al usuario de todos los canales
        for channel_name in channels.values():
            if websocket in channel_name:
                channel_name.remove(websocket)

async def notify_channel(channel, message):
    """Notifica a todos los usuarios en un canal."""
    if channel in channels:
        websockets_in_channel = channels[channel]
        if websockets_in_channel:
            await asyncio.wait([ws.send(message) for ws in websockets_in_channel])

# Iniciar el servidor WebSocket
start_server = websockets.serve(handler, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
