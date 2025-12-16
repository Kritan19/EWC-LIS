import socket

# ASTM control characters
STX = b'\x02'
ETX = b'\x03'
ENQ = b'\x05'
ACK = b'\x06'
EOT = b'\x04'
CR = b'\x0D'

HOST = '127.0.0.1'
PORT = 5000


# --------------------------------------
# Helper to calculate LRC (XOR of all bytes between STX and ETX)
# --------------------------------------
def calc_lrc(payload: bytes):
    val = 0
    for b in payload:
        val ^= b
    return bytes([val])


# --------------------------------------
# Build ASTM frame
# --------------------------------------
def build_frame(text: str) -> bytes:
    payload = text.encode('utf-8')
    lrc = calc_lrc(payload)
    return STX + payload + ETX + lrc + CR


# --------------------------------------
# Two sample messages
# --------------------------------------
frames = [
    # Sample 1: Patient Surya
    "1H|\\^&|||UIW_LIS|||||LIS_ID||P||20251111161326\r"
    "P|1|2500077324|||Tamang^Surya^Bahadur||20011111|M\r"
    "O|1|0105914900^CM031728^6||^^^UN_c^^^1^^\\^^^TP_2^^^1^^\\^^^Alb^^^1^^\\^^^FT3^^^1^^\\^^^FT4^^^1^^\\^^^Crea_2^^^1^^\\^^^TBil_2^^^1^^\\^^^DBil_2^^^1^^\\^^^AST^^^1^^\\^^^ALP_2c^^^1^^\\^^^ALT^^^1|R|20251111155510|||||||||Serum^^^1||||||||||F\r"
    # "O|1|0105914900^CM031728^6||^^^UN_c^^^1^^\\^^^TP_2^^^1\r"
    "R|1|^^^Alb^^^1^RLU^79744#0|408.4915|||||F\r"
    "R|2|^^^Alb^^^1^DOSE^79744#0|4.8|g/dL||||F\\R||LabManager^System||20251111160746|IRL011842443^IRC012402443\r",

    # Sample 2: Patient unknown

    "1H|\\^&|||UIW_LIS|||||LIS_ID||P||20251111161500\r"
    "P|2|2500077325|||||F\r"
    "O|2|0105914901^CM031729^6||^^^UN_c^^^1^^\\^^^TP_2^^^1\r"
    "R|1|^^^Iron3^^^1^RLU^28819#0|31.4807|||||F\r"
    "R|2|^^^Alb^^^1^DOSE^79744#0|4.8|g/dL||||F\\R||LabManager^System||20251111160746|IRL011842443^IRC012402443\r",

    "1H|\\^&|||UIW_LIS|||||LIS_ID||P||20251111161500\r"
    "P|2|2500077326|||||F\r"
    "O|2|0105914902^CM031728^6||^^^UN_c^^^1^^\\^^^TP_2^^^1\r"
    "R|1|^^^Iron3^^^1^RLU^28819#0|31.4807|||||F\r"
    "R|2|^^^Alb^^^1^DOSE^79744#0|4.8|g/dL||||F\\R||LabManager^System||20251111160746|IRL011842443^IRC012402443\r"

 ]

# --------------------------------------
# Connect and send
# --------------------------------------
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print("Connected to listener")

    # Handshake ENQ → ACK
    s.sendall(ENQ)
    resp = s.recv(1024)
    if resp == ACK:
        print("Handshake OK")
    else:
        print("Handshake failed")

    # Send frames
    for frame_text in frames:
        frame = build_frame(frame_text)
        s.sendall(frame)
        print(f"Sent frame:\n{frame_text}")
        # Wait for ACK
        resp = s.recv(1024)
        if resp == ACK:
            print("Frame ACK received")
        else:
            print("No ACK")

    # End transmission
    s.sendall(EOT)
    print("Sent EOT")

