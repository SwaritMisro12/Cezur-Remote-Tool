import socket
import cv2
import numpy as np
from io import BytesIO
import zlib
import tkinter as tk
from PIL import Image, ImageTk

SERVER_IP = '127.0.0.1'
SERVER_PORT = 55555

def receive_frame(client_socket):
    compressed_data = b''
    while True:
        data = client_socket.recv(4096)
        if not data:
            break
        compressed_data += data

        # Check for the end of a frame marker (adjust as needed)
        if b'END_OF_FRAME' in compressed_data:
            break

    try:
        # Remove the marker and decompress the data
        compressed_data = compressed_data.replace(b'END_OF_FRAME', b'')
        img_bytes = zlib.decompress(compressed_data)
        img_data = np.load(BytesIO(img_bytes))
        frame = cv2.imdecode(img_data['img_encoded'], 1)
        return frame
    except zlib.error as e:
        print(f"Error decompressing data: {e}")
        return None

def send_frame(client_socket, frame):
    if frame is not None and isinstance(frame, np.ndarray):
        _, img_encoded = cv2.imencode('.png', frame)
        img_bytes = BytesIO()
        np.savez_compressed(img_bytes, img_encoded=img_encoded)
        compressed_data = zlib.compress(img_bytes.getvalue())
        client_socket.sendall(compressed_data + b'END_OF_FRAME')
    else:
        print("Invalid frame")
        if frame is None:
            print("Frame is None")
        else:
            print(f"Frame type: {type(frame)}")

class App:
    def __init__(self, root, server_ip, server_port):
        self.root = root
        self.root.title("Phone Screen Viewer")

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((server_ip, server_port))

        self.label = tk.Label(root)
        self.label.pack()

        self.update()

    def update(self):
        frame = receive_frame(self.client_socket)
        if frame is not None:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img = ImageTk.PhotoImage(img)
            self.label.config(image=img)
            self.label.image = img

        self.root.after(10, self.update)  # Update every 10 milliseconds

    def run(self):
        self.root.mainloop()

def main():
    root = tk.Tk()
    app = App(root, SERVER_IP, SERVER_PORT)
    app.run()

if __name__ == "__main__":
    main()
