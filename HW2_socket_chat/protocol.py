import struct


MAX_MESSAGE_SIZE = 10 * 1024 * 1024

COMMAND_SIZE = 8
LENGTH_SIZE = 4


def recv_exact(sock, size):
    data = bytearray()

    while len(data) < size:
        chunk = sock.recv(size - len(data))

        if chunk == b"":
            raise ConnectionError(
                "Connection closed before all data was received"
            )

        data.extend(chunk)

    return bytes(data)


def send_message(sock, command: str, payload: bytes = b""):
    command_bytes = command.encode("utf-8")

    if len(command_bytes) > COMMAND_SIZE:
        raise ValueError("Command is too long")

    if len(payload) > MAX_MESSAGE_SIZE:
        raise ValueError("Message is too large")

    # Дополняем команду до 8 байт
    command_bytes = command_bytes.ljust(COMMAND_SIZE, b"\x00")

    # Длина payload занимает 4 байта
    length_bytes = struct.pack("!I", len(payload))

    message = command_bytes + length_bytes + payload

    sock.sendall(message)


def recv_message(sock):
    # Первый recv делаем отдельно,
    # чтобы корректно определить штатное закрытие соединения
    command_bytes = sock.recv(COMMAND_SIZE)

    if command_bytes == b"":
        return None

    # Если команда пришла кусками
    if len(command_bytes) < COMMAND_SIZE:
        command_bytes += recv_exact(
            sock,
            COMMAND_SIZE - len(command_bytes)
        )

    # Убираем добавленные \x00
    command = command_bytes.rstrip(b"\x00").decode("utf-8")

    length_bytes = recv_exact(sock, LENGTH_SIZE)
    length = struct.unpack("!I", length_bytes)[0]

    if length > MAX_MESSAGE_SIZE:
        raise ValueError("Message is too large")

    if length == 0:
        payload = b""
    else:
        payload = recv_exact(sock, length)

    return command, payload