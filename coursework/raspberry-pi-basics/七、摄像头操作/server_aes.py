import cv2
import socket
import struct
import numpy as np
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# Configuration parameters
SERVER_PORT = 9999
AES_KEY = b'CHANGE_THIS_KEY!'

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('', SERVER_PORT))

print(f"Server started, listening on port {SERVER_PORT}...")

try:
    current_frame = -1
    chunks = {}
    total_size = 0
    
    while True:
        data, addr = server_socket.recvfrom(65535)
        
        if len(data) < 8:
            continue
        
        # Parse frame number and sequence
        frame_num, seq = struct.unpack('!II', data[:8])
        
        # New frame
        if frame_num != current_frame:
            current_frame = frame_num
            chunks = {}
            print(f"\n📦 Receiving frame {frame_num}...")
        
        # End marker
        if seq == 0xFFFFFFFF:
            print(f"✅ Frame {frame_num} complete, total chunks: {len(chunks)}")
            
            # Reassemble packet
            packet = b''
            for i in sorted(chunks.keys()):
                packet += chunks[i]
            
            if len(packet) < 16:
                print("⚠️ Packet too small")
                continue
            
            # Extract IV and encrypted data
            iv = packet[:16]
            encrypted_data = packet[16:]
            
            # Check if encrypted data length is valid
            if len(encrypted_data) % 16 != 0:
                print(f"⚠️ Invalid encrypted data length: {len(encrypted_data)}")
                continue
            
            # AES decryption
            try:
                cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
                decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
                
                # Decode image
                nparr = np.frombuffer(decrypted_data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if frame is not None:
                    cv2.putText(frame, f"Server - Frame {frame_num} | LiuShengwei-0000000000", 
                                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    cv2.imshow('Server - Received', frame)
                else:
                    print("❌ Failed to decode image")
                    
            except ValueError as e:
                print(f"❌ Decryption error: {e}")
            except Exception as e:
                print(f"❌ Error: {e}")
        else:
            # Store chunk
            chunks[seq] = data[8:]
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("\nServer closed")
finally:
    cv2.destroyAllWindows()
    server_socket.close()