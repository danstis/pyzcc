import asyncio
import pyzcc

found_devices = asyncio.run(pyzcc.Discover.discover())
for device in found_devices:
    print(device)
