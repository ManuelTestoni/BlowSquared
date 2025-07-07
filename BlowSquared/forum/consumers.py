import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import MessaggioForum
from negozi.models import Negozio
from prodotti.models import Prodotto

class ForumConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Tutti gli utenti autenticati si uniscono alla stessa room
        self.room_name = 'forum_generale'
        self.room_group_name = f'forum_{self.room_name}'
        
        # Verifica autenticazione
        if self.scope["user"].is_anonymous:
            await self.close()
            return
        
        # Unisciti al gruppo
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Invia messaggi recenti all'utente che si connette
        messaggi_recenti = await self.get_messaggi_recenti()
        for messaggio in messaggi_recenti:
            await self.send(text_data=json.dumps({
                'tipo': 'messaggio_storico',
                'messaggio': messaggio
            }))
    
    async def disconnect(self, close_code):
        # Lascia il gruppo
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        
        if data['tipo'] == 'chat':
            await self.handle_chat_message(data)
        elif data['tipo'] == 'recensione':
            await self.handle_recensione(data)
        elif data['tipo'] == 'ricetta':
            await self.handle_ricetta(data)
    
    async def handle_chat_message(self, data):
        """Gestisce messaggi di chat normale"""
        messaggio = await self.create_messaggio(
            tipo='chat',
            contenuto=data['contenuto']
        )
        
        if messaggio:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'forum_message',
                    'messaggio': messaggio.to_dict()
                }
            )
    
    async def handle_recensione(self, data):
        """Gestisce recensioni negozi"""
        messaggio = await self.create_messaggio(
            tipo='recensione',
            contenuto=data['contenuto'],
            negozio_id=data.get('negozio_id'),
            stelle=data.get('stelle')
        )
        
        if messaggio:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'forum_message',
                    'messaggio': messaggio.to_dict()
                }
            )
    
    async def handle_ricetta(self, data):
        """Gestisce condivisione ricette"""
        messaggio = await self.create_messaggio(
            tipo='ricetta',
            contenuto=data.get('contenuto', ''),
            nome_ricetta=data.get('nome_ricetta'),
            ingredienti=data.get('ingredienti', []),
            note_ricetta=data.get('note_ricetta', '')
        )
        
        if messaggio:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'forum_message',
                    'messaggio': messaggio.to_dict()
                }
            )
    
    async def forum_message(self, event):
        """Invia messaggio a WebSocket"""
        await self.send(text_data=json.dumps({
            'tipo': 'nuovo_messaggio',
            'messaggio': event['messaggio']
        }))
    
    @database_sync_to_async
    def create_messaggio(self, tipo, contenuto, **kwargs):
        """Crea nuovo messaggio nel database"""
        try:
            messaggio_data = {
                'autore': self.scope["user"],
                'tipo': tipo,
                'contenuto': contenuto,
            }
            
            if tipo == 'recensione':
                if kwargs.get('negozio_id'):
                    negozio = Negozio.objects.get(id=kwargs['negozio_id'])
                    messaggio_data['negozio_recensito'] = negozio
                messaggio_data['stelle'] = kwargs.get('stelle')
            
            elif tipo == 'ricetta':
                messaggio_data['nome_ricetta'] = kwargs.get('nome_ricetta')
                messaggio_data['ingredienti_ricetta'] = kwargs.get('ingredienti', [])
                messaggio_data['note_ricetta'] = kwargs.get('note_ricetta', '')
            
            return MessaggioForum.objects.create(**messaggio_data)
            
        except Exception as e:
            print(f"Errore creazione messaggio: {e}")
            return None
    
    @database_sync_to_async
    def get_messaggi_recenti(self):
        """Recupera ultimi 50 messaggi"""
        messaggi = MessaggioForum.objects.select_related(
            'autore', 'negozio_recensito'
        ).order_by('-data_creazione')[:50]
        
        return [msg.to_dict() for msg in reversed(messaggi)]
