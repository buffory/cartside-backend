import asyncio
import websockets
import json

async def test_websockets():
    uri = "ws://127.0.0.1:33703/devtools/browser/74b9a020-6e84-46e9-845b-3c7f75656742"
    async with websockets.connect(uri) as websocket:
        enable_cmd = {
                "id": 1,
                "method": "Runtime.enable",
            }
        await websocket.send(json.dumps(enable_cmd))
        response = await websocket.recv()
        print("Response:",json.loads(response))

        eval_cmd = {
                "id": 2,
                "method": "Runtime.evaluate",
                "params": {
                    "expression": "navigator.userAgent",
                    "userGesture": True,
                    "awaitPromise": True,
                    "returnByValue": True,
                    "allowUnsafeEvalBlockedByCSP": True
                    }
                    
            }
        await websocket.send(json.dumps(eval_cmd))
        response = await websocket.recv()
        print("Response:",json.loads(response))
        

asyncio.run(test_websockets())
