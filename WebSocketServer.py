"""
WebSocket Server for Real-time Monitor System
Provides real-time updates to connected clients via WebSocket
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Set
import websockets
from websockets.server import WebSocketServerProtocol

from RealTimeMonitor import get_rms_instance

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebSocketServer:
    """WebSocket server for broadcasting real-time updates"""
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.clients: Set[WebSocketServerProtocol] = set()
        self.rms = get_rms_instance()
        
    async def register_client(self, websocket: WebSocketServerProtocol):
        """Register a new client connection"""
        self.clients.add(websocket)
        logger.info(f"Client connected. Total clients: {len(self.clients)}")
        
        # Send initial data
        try:
            initial_data = {
                'type': 'initial',
                'data': self.rms.get_all_accounts_snapshot(),
                'stats': self.rms.get_stats(),
                'timestamp': datetime.now().isoformat()
            }
            await websocket.send(json.dumps(initial_data, default=str))
        except Exception as e:
            logger.error(f"Error sending initial data: {e}")
    
    async def unregister_client(self, websocket: WebSocketServerProtocol):
        """Unregister a client connection"""
        self.clients.discard(websocket)
        logger.info(f"Client disconnected. Total clients: {len(self.clients)}")
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        if not self.clients:
            return
        
        message_json = json.dumps(message, default=str)
        disconnected = set()
        
        for client in self.clients:
            try:
                await client.send(message_json)
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(client)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected.add(client)
        
        # Remove disconnected clients
        for client in disconnected:
            await self.unregister_client(client)
    
    async def handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """Handle individual client connection"""
        await self.register_client(websocket)
        
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.handle_message(websocket, data)
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'message': 'Invalid JSON'
                    }))
                except Exception as e:
                    logger.error(f"Error handling message: {e}")
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'message': str(e)
                    }))
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister_client(websocket)
    
    async def handle_message(self, websocket: WebSocketServerProtocol, data: dict):
        """Handle messages from clients"""
        msg_type = data.get('type')
        
        if msg_type == 'add_account':
            login_id = data.get('login_id')
            if login_id:
                self.rms.add_account(int(login_id))
                await websocket.send(json.dumps({
                    'type': 'success',
                    'message': f'Account {login_id} added to monitoring'
                }))
        
        elif msg_type == 'remove_account':
            login_id = data.get('login_id')
            if login_id:
                self.rms.remove_account(int(login_id))
                await websocket.send(json.dumps({
                    'type': 'success',
                    'message': f'Account {login_id} removed from monitoring'
                }))
        
        elif msg_type == 'get_snapshot':
            login_id = data.get('login_id')
            if login_id:
                snapshot = self.rms.get_account_snapshot(int(login_id))
                await websocket.send(json.dumps({
                    'type': 'snapshot',
                    'data': snapshot,
                    'timestamp': datetime.now().isoformat()
                }, default=str))
            else:
                snapshot = self.rms.get_all_accounts_snapshot()
                await websocket.send(json.dumps({
                    'type': 'snapshot',
                    'data': snapshot,
                    'timestamp': datetime.now().isoformat()
                }, default=str))
        
        elif msg_type == 'get_exposure':
            symbol = data.get('symbol')
            if symbol:
                positions = self.rms.get_positions_by_symbol(symbol)
                await websocket.send(json.dumps({
                    'type': 'exposure',
                    'symbol': symbol,
                    'positions': positions,
                    'timestamp': datetime.now().isoformat()
                }, default=str))
            else:
                exposure = self.rms.get_total_exposure_by_symbol()
                await websocket.send(json.dumps({
                    'type': 'exposure',
                    'data': exposure,
                    'timestamp': datetime.now().isoformat()
                }, default=str))
        
        elif msg_type == 'get_stats':
            stats = self.rms.get_stats()
            await websocket.send(json.dumps({
                'type': 'stats',
                'data': stats,
                'timestamp': datetime.now().isoformat()
            }, default=str))
        
        else:
            await websocket.send(json.dumps({
                'type': 'error',
                'message': f'Unknown message type: {msg_type}'
            }))
    
    def on_data_update(self, accounts_data: list):
        """Callback for when RMS updates data"""
        message = {
            'type': 'update',
            'data': accounts_data,
            'timestamp': datetime.now().isoformat()
        }
        
        # Schedule broadcast in the event loop
        asyncio.create_task(self.broadcast(message))
    
    async def start(self):
        """Start the WebSocket server"""
        # Initialize and start RMS
        if not self.rms.initialize():
            logger.error("Failed to initialize RMS")
            return
        
        # Add callback for updates
        self.rms.add_callback(self.on_data_update)
        
        # Start RMS monitoring
        self.rms.start()
        
        # Start WebSocket server
        logger.info(f"Starting WebSocket server on {self.host}:{self.port}")
        async with websockets.serve(self.handle_client, self.host, self.port):
            await asyncio.Future()  # Run forever
    
    def run(self):
        """Run the WebSocket server"""
        try:
            asyncio.run(self.start())
        except KeyboardInterrupt:
            logger.info("Shutting down WebSocket server")
            self.rms.stop()


if __name__ == "__main__":
    server = WebSocketServer(host="0.0.0.0", port=8765)
    server.run()
