import time
import json
import os
import asyncio
from pathlib import Path

def check_local_model() -> None:
    """
    Checks for the existence of a model configuration file and prints the status of each model.
    """
    try:
        exo_cache = Path.home() / '.cache' / 'exo'
        config_path = exo_cache / 'model_config.txt'
        if not config_path.exists():
            print(f"\n=== Model Config Check ===")
            print("model_config.txt not found in ~/.cache/exo")
            print("=======================\n")
            return
        
        with open(config_path, 'r') as f:
            model_configs = f.read().splitlines()

        print(f"\n=== Model Config Check ===")
        for config in model_configs:
            if not config:
                continue
            model_name = config.split(':')[0]
            model_path = config.split(':')[-1]
            model_dir = Path(model_path)
            
            if model_dir.exists():
                print(f" {model_name}: Found at {model_path}")
            else:
                print(f" {model_name}: Not found at {model_path}")
        print("=======================\n")
    except Exception as e:
        print(f"An error occurred: {e}")

async def print_node_network(server) -> None:
    """
    Periodically prints the network nodes information and broadcasts it to connected peers.
    """
    try:
        last_network_time = 0
        await check_model_config()  # Run initial check
        
        while True:
            current_time = time.time()
            if current_time - last_network_time >= 3.0:
                last_network_time = current_time
                network_info = {
                    "type": "network_info",
                    "current_node": {
                        "id": server.node.id,
                        "address": f"{server.host}:{server.port}"
                    },
                    "peers": [{"id": peer.id(), "address": peer.addr()} for peer in server.node.peers]
                }
                print("\n=== Network Nodes Information ===")
                print(f"Current Node: {network_info['current_node']['id']} @ {network_info['current_node']['address']}")
                print("Connected Peers:")
                for peer in network_info['peers']:
                    print(f"- {peer['id']} @ {peer['address']}")
                print("================================\n")
                await server.node.broadcast_opaque_status("", json.dumps(network_info))
                await check_model_config()  # Run periodic check
            await asyncio.sleep(1)
    except Exception as e:
        print(f"An error occurred: {e}")
