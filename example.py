import asyncio
import logging
import pyzcc

logging.basicConfig(level=logging.DEBUG)

found_devices = asyncio.run(pyzcc.Discover.discover())
for device in found_devices:
    print(device)
