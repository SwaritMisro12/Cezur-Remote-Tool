import socket
import cv2
import numpy as np
from io import BytesIO
import zlib
from PIL import ImageGrab  # Pillow library for screen capture
import keyboard

HOST = '127.0.0.1'
PORT = 55555

def send_frame_and_commands(conn, frame):
    if frame is not None and isinstance(frame, np.ndarray):
        _, img_encoded = cv2.imencode('.png', frame)
        img_bytes = BytesIO()
        np.savez_compressed(img_bytes, img_encoded=img_encoded)
        compressed_data = zlib.compress(img_bytes.getvalue())
        conn.sendall(compressed_data + b'END_OF_FRAME')

        # Capture keyboard events
        events = keyboard.record(until='esc')  # Record events until the 'esc' key is pressed
        commands_str = "|".join(str(event) for event in events)
        conn.sendall(commands_str.encode() + b'END_OF_COMMANDS')
    else:
        print("Invalid frame")
        if frame is None:
            print("Frame is None")
        else:
            print(f"Frame type: {type(frame)}")

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()

        print(f"Server listening on {HOST}:{PORT}")

        conn, addr = server_socket.accept()
        with conn:
            print(f"Connected by {addr}")

            while True:
                frame = ImageGrab.grab().convert('RGB')  # Use Pillow for screen capture
                frame = np.array(frame)
                send_frame_and_commands(conn, frame)

if __name__ == "__main__":
    main()
