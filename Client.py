import socket
import json
import tkinter as tk
import tkinter.scrolledtext as scrolledTextWidget
import time 
import threading


##TODO Add column in middle for send button and name. or put send below server/port and name inside 
##TODO Change timestamp to GMT and then back to local time so we all use common time
##TODO Add scroll bar to listbox
##TODO Add ability to hit enter to send message
##TODO Create Textbox to show and change when connected to server 
##TODO Handle receiving bulk messages on connection to server 
message = {
    "Timestamp": None,
    "Name": None,
    "Content": None
}


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Client")
    root.geometry("1000x650")
    
    client_connection = None

    
    message_data = []
    
    channel_data = []
    
    text_content = tk.StringVar()
    name_content = tk.StringVar()
    server_IP = tk.StringVar(value="192.168.0.80")
    server_Port = tk.IntVar(value=9090)
    
    def get_time():
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    
    ## Create Connection Entry area
    
    connection_frame = tk.Frame(root)
    connection_frame.grid(row=0, column=0, padx=10, pady=10)
    
    
    server_ip_label = tk.Label(connection_frame, text="Server IP:")
    server_ip_label.grid(row=0, column=0, padx=5, sticky="e")
    
    server_ip_address = tk.Entry(connection_frame, textvariable=server_IP, width=20)
    server_ip_address.grid(row=0, column=1, padx=5, sticky="w")
    
    server_port_label = tk.Label(connection_frame, text="Port:")
    server_port_label.grid(row=1, column=0, padx=5, sticky="e")
    
    server_port = tk.Entry(connection_frame, textvariable=server_Port, width=10)
    server_port.grid(row=1, column=1, padx=5, sticky="w")
    
    user_name_label = tk.Label(connection_frame, text="Name:")
    user_name_label.grid(row=2, column=0, padx=5, sticky="e")
    
    user_name = tk.Entry(connection_frame, textvariable=name_content, width=20)
    user_name.grid(row=2, column=1, padx=5, sticky="w")
    
    
    def handle_client(conn, addr):
        global client_connection
        client_connection = conn
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                message_data.append(data.decode('utf-8'))
                ##TODO Update listbox from message_data storage. Probably somewhere else 
                ##chat_list_box.insert(tk.END, data.decode('utf-8'))
        except Exception as e:
            print(f"Error handling client {addr}: {e}")
        finally:
            conn.close()
            client_connection = None
    
    def connect_to_server():
        global client_connection
        try:
            client_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_connection.connect((server_IP.get(), server_Port.get()))
            threading.Thread(target=receive_messages, daemon=True).start()
            print("Connected to server.")
        except Exception as e:
            print(f"Connection error: {e}")
            client_connection = None
        
    def receive_messages():
        global client_connection

            
        try:
            while True:
                data = client_connection.recv(4096)
                if not data:
                    break
                text = data.decode('utf-8')
    
                try:
                    message_object = json.loads(text)
                except Exception as e:
                    print(f"JSON decode error: {e}")
                    continue
                
                # helper to append a line and scroll
                def append_line(line):
                    chat_list_box.insert(tk.END, line + "\n")
                    chat_list_box.see(tk.END)
    
                if isinstance(message_object, dict):
                    formatted = f"[{message_object.get('Timestamp')}]<{message_object.get('Name')}>: {message_object.get('Content')}"
                    root.after(0, append_line, formatted)
                elif isinstance(message_object, list):
                    def populate_channels(channels):
                        channel_list_box.delete(0, tk.END)
                        for channel in channels:
                            channel_list_box.insert(tk.END, channel)
                    root.after(0, populate_channels, message_object)
                        
        except Exception as e: 
            print(f"Error receiving messages: {e}")
        finally:
            client_connection.close()
            client_connection = None
            
    connect_button = tk.Button(connection_frame, text="Connect", command=connect_to_server)
    connect_button.grid(row=3, column=0, columnspan=2, pady=5)
    
    channel_list_box = tk.Listbox(root, width=20, height=20)
    channel_list_box.grid(row=4, column=0, rowspan=2, padx=10, pady=10)
            
    def send_message():
        global client_connection
        if client_connection:
            try:
                message["Name"] = name_content.get()
                message["Content"] = text_content.get()
                message["Timestamp"] = get_time()
                message_json = json.dumps(message) + "\n"
                client_connection.sendall(message_json.encode('utf-8'))
                
                text_content.set("")
                
            except Exception as e:
                print(f"Error sending message: {e}")
        else:
            print("Not connected to server.")
            
    
    
    chat_list_box = scrolledTextWidget.ScrolledText(root, width=50, height=20)
    chat_list_box.grid(row=0, column=1, columnspan=2, rowspan=2, padx=10, pady=10) 
    

    
    text_input = tk.Entry(root,textvariable = text_content, width=50)
    text_input.grid(row=2, column=1,columnspan=2, padx=10, pady=10)
    

    
    
    send_button = tk.Button(root, text="Send", command=send_message)
    send_button.grid(row=2, column=0, padx=10, pady=10)
    
    
    
    root.mainloop()
