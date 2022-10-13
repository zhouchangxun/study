import datetime
import asyncio

async def handle_echo(reader, writer):
  addr = writer.get_extra_info('peername')
  addr = f'{addr[0]}:{addr[1]}'
  print(f"new conn from [{addr}]")

  while True:
    data = await reader.read(100)
    if not data:
      print(f"[{addr}] Close the connection")
      writer.close()
      break

    t = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    message = data.decode()
    print(f"[{t}] [{addr}] recv: {message!r}")
    print(f"[{t}] [{addr}] send: {message!r}")
    writer.write(data)
    await writer.drain()


async def main():
    server = await asyncio.start_server(handle_echo, '0.0.0.0', 6666)

    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f'Serving on {addrs}')

    async with server:
        await server.serve_forever()

try:
  asyncio.run(main())
except KeyboardInterrupt:
  print('\nExited.')
