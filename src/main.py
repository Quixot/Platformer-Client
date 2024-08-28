import asyncio
import json
import pygame
import websockets
import random

colors = [(255, 0, 0), (0, 255, 0)]

async def send_message(websocket, message):
    await websocket.send(json.dumps(message))

async def receive_updates(websocket, players):
    while True:
        message = await websocket.recv()
        data = json.loads(message)
        if data["action"] == "update":
            players[:] = data["players"]

async def game_loop():
    uri = "ws://127.0.0.1:8000/ws"
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Multiplayer Game Client")

    players = []

    async with websockets.connect(uri) as websocket:
        asyncio.create_task(receive_updates(websocket, players))

        # Создаем словарь для отслеживания нажатых клавиш
        keys = {"left": False, "right": False, "jump": False}

        async def handle_movement():
            while True:
                if keys["left"]:
                    await send_message(websocket, {"action": "move_left"})
                if keys["right"]:
                    await send_message(websocket, {"action": "move_right"})
                if keys["jump"]:
                    await send_message(websocket, {"action": "jump"})
                await asyncio.sleep(0.05)  # Небольшая задержка для плавности

        asyncio.create_task(handle_movement())  # Отдельная задача для обработки движения

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        keys["jump"] = True
                    elif event.key == pygame.K_a:
                        keys["left"] = True
                    elif event.key == pygame.K_d:
                        keys["right"] = True
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_w:
                        keys["jump"] = False
                    elif event.key == pygame.K_a:
                        keys["left"] = False
                    elif event.key == pygame.K_d:
                        keys["right"] = False

            screen.fill((0, 0, 0))
            for color, player in enumerate(players):
                pygame.draw.rect(screen, colors[color], pygame.Rect(player["x"], player["y"], 50, 50))

            pygame.display.flip()
            await asyncio.sleep(0.001)

    pygame.quit()

asyncio.run(game_loop())
