import socket
import threading

from protocol import send_message, recv_message


HOST = "127.0.0.1"
PORT = 8000


running = threading.Event()
running.set()


def receive_messages(sock):
    try:
        while running.is_set():

            message = recv_message(sock)

            if message is None:
                print("\nСервер закрыл соединение")
                break

            command, payload = message

            text = payload.decode(
                "utf-8",
                errors="replace"
            )

            if command == "TEXT":
                print(f"\n{text}")

            elif command == "LIST":
                print("\nПользователи:")

                if text:
                    print(text)
                else:
                    print("(нет пользователей)")

            elif command == "JOIN":
                print(f"\n{text}")

            elif command == "ERROR":
                print(f"\nОшибка: {text}")

            elif command == "QUIT":
                print("\nСервер подтвердил выход")
                break

    except ConnectionResetError:
        print("\nСоединение с сервером сброшено")

    except ConnectionError as error:
        print("\nСоединение закрыто:", error)

    except OSError as error:
        if running.is_set():
            print("\nОшибка сети:", error)

    finally:
        running.clear()


def main():

    client = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    try:
        client.connect((HOST, PORT))

    except ConnectionRefusedError:
        print("Сервер недоступен")
        client.close()
        return

    try:
        username = input("Введите имя: ").strip()

        send_message(
            client,
            "JOIN",
            username.encode("utf-8")
        )

        receiver_thread = threading.Thread(
            target=receive_messages,
            args=(client,),
            daemon=True
        )

        receiver_thread.start()

        print("Команды:")
        print("/list - список пользователей")
        print("/quit - выйти")
        print("Любой другой текст отправляется как сообщение")

        while running.is_set():

            text = input("> ")

            if text.strip() == "/list":

                send_message(
                    client,
                    "LIST",
                    b""
                )

            elif text.strip() == "/quit":

                send_message(
                    client,
                    "QUIT",
                    b""
                )

                break

            else:

                send_message(
                    client,
                    "TEXT",
                    text.encode("utf-8")
                )

    except BrokenPipeError:
        print("Нельзя отправить данные: соединение закрыто")

    except ConnectionResetError:
        print("Соединение с сервером сброшено")

    except OSError as error:
        print("Ошибка сети:", error)

    finally:

        running.clear()

        try:
            client.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass

        client.close()


if __name__ == "__main__":
    main()