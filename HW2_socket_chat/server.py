import socket
import threading

from protocol import send_message, recv_message


HOST = "127.0.0.1"
PORT = 8000


# socket -> username
clients = {}

clients_lock = threading.Lock()
send_lock = threading.Lock()


def safe_send(sock, command, payload=b""):
    with send_lock:
        send_message(sock, command, payload)


def broadcast(command, payload, exclude=None):
    with clients_lock:
        sockets = list(clients.keys())

    for client_socket in sockets:
        if client_socket is exclude:
            continue

        try:
            safe_send(client_socket, command, payload)

        except (BrokenPipeError, ConnectionResetError, OSError):
            pass


def handle_client(conn, addr):
    username = None

    print("Клиент подключился:", addr)

    try:
        while True:
            message = recv_message(conn)

            # recv() == b""
            if message is None:
                print("Клиент штатно закрыл соединение:", addr)
                break

            command, payload = message


            if command == "JOIN":

                if username is not None:
                    safe_send(
                        conn,
                        "ERROR",
                        "Вы уже зарегистрированы".encode("utf-8")
                    )
                    continue

                new_username = payload.decode("utf-8").strip()

                if not new_username:
                    safe_send(
                        conn,
                        "ERROR",
                        "Имя не может быть пустым".encode("utf-8")
                    )
                    continue

                with clients_lock:
                    username_taken = new_username in clients.values()

                    if not username_taken:
                        clients[conn] = new_username
                        username = new_username

                if username_taken:
                    safe_send(
                        conn,
                        "ERROR",
                        "Это имя уже занято".encode("utf-8")
                    )
                    continue

                safe_send(
                    conn,
                    "JOIN",
                    f"Вы вошли как {username}".encode("utf-8")
                )

                broadcast(
                    "TEXT",
                    f"[system] {username} подключился".encode("utf-8"),
                    exclude=conn
                )

                print(f"{addr} теперь пользователь {username}")


            elif command == "TEXT":

                if username is None:
                    safe_send(
                        conn,
                        "ERROR",
                        "Сначала нужно выполнить JOIN".encode("utf-8")
                    )
                    continue

                text = payload.decode("utf-8")

                print(f"{username}: {text}")

                broadcast(
                    "TEXT",
                    f"{username}: {text}".encode("utf-8"),
                    exclude=conn
                )


            elif command == "LIST":

                with clients_lock:
                    usernames = sorted(clients.values())

                data = "\n".join(usernames).encode("utf-8")

                safe_send(
                    conn,
                    "LIST",
                    data
                )


            elif command == "QUIT":

                safe_send(conn, "QUIT", b"")
                break


            else:

                safe_send(
                    conn,
                    "ERROR",
                    f"Неизвестная команда: {command}".encode("utf-8")
                )

    except ConnectionResetError:
        print("ConnectionResetError:", addr)

    except BrokenPipeError:
        print("BrokenPipeError:", addr)

    except ConnectionError as error:
        print("ConnectionError:", addr, error)

    except ValueError as error:
        print("Ошибка протокола:", error)

        try:
            safe_send(
                conn,
                "ERROR",
                str(error).encode("utf-8")
            )
        except OSError:
            pass

    except OSError as error:
        print("OSError:", addr, error)

    finally:

        disconnected_username = username

        with clients_lock:
            clients.pop(conn, None)

        conn.close()

        if disconnected_username is not None:

            broadcast(
                "TEXT",
                f"[system] {disconnected_username} вышел".encode("utf-8")
            )

        print("Клиент отключён:", addr)


def main():
    server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    server.bind((HOST, PORT))

    server.listen()

    print(f"Сервер запущен: {HOST}:{PORT}")

    try:
        while True:

            conn, addr = server.accept()

            thread = threading.Thread(
                target=handle_client,
                args=(conn, addr),
                daemon=True
            )

            thread.start()

    except KeyboardInterrupt:
        print("\nСервер остановлен")

    finally:
        server.close()


if __name__ == "__main__":
    main()