import socket

ENQ = b'\x05'
ACK = b'\x06'
EOT = b'\x04'
STX = b'\x02'
ETX = b'\x03'
CR  = b'\x0D'

HOST = '127.0.0.1'
PORT = 8002

astm_message = (
    # NMC SAMPLE

    "1H|\\^&|||UIW_LIS|||||LIS_ID||P||20251111161326\r"
    "P|1|2500077324|||Tamang^Surya^Bahadur||20240110|M\r"
    "O|1|0105914900^CM031728^6||^^^UN_c^^^1^^\\^^^TP_2^^^1^^\\^^^Alb^^^1^^\\^^^FT3^^^1^^\\^^^FT4^^^1^^\\^^^Crea_2^^^1^^\\^^^TBil_2^^^1^^\\^^^DBil_2^^^1^^\\^^^AST^^^1^^\\^^^ALP_2c^^^1^^\\^^^ALT^^^1|R|20251111155510|||||||||Serum^^^1||||||||||F\r"
    "R|1|^^^Alb^^^1^RLU^79744#0|408.4915|||||F\\R||LabManager^System||20251111160746|IRL011842443^IRC012402443\r"
    "R|2|^^^Alb^^^1^DOSE^79744#0|4.8|g/dL||||F\\R||LabManager^System||20251111160746|IRL011842443^IRC012402443\r"
    "L|1|N"

    #NPL SAMPLE 1

    # "1H|\^&|||UIW_LIS|||||LIS_ID||P||20251118162315\r"
    # "P|1|BC01918701||||||U|||||201\r"
    # "O|1|BC01918701^AG031665^1||^^^Iron3^^^1|R|20251118142521|||||||||Serum^^^1||||||||||F\r"
    # "R|1|^^^Iron3^^^1^RLU^28819#0|31.4807|||||F\\R||CSE^System||20251118143620|IRL005\r"
    # "L|1|N"

    #NPL SAMPLE 2

# "29392415^IRC009382415\r"
# "C|1||PREAG^140136|G\r"
# "R|2|^^^Iron3^^^1^DOSE^28819#0|52|ug/dL|[ Normal : 50 - 175 ]|||F\R||CSE^System||20251118143620|IRL009392415^IRC009382415\r"
# "C|1||PREAG^140136|G\r"
# "L|1|N"
)

def checksum(frame_bytes):
    cs = sum(frame_bytes) & 0xFF
    return cs.to_bytes(1, 'big')

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    # Send ENQ and wait for ACK
    s.sendall(ENQ)
    ack = s.recv(1024)
    if ack != ACK:
        print("Listener not ready")
        exit()

    # Build ASTM frame
    frame_bytes = astm_message.encode()
    cs = checksum(frame_bytes)
    frame = STX + frame_bytes + ETX + cs + CR

    s.sendall(frame)
    ack = s.recv(1024)
    if ack == ACK:
        print("Frame accepted by listener")

    # End of transmission
    s.sendall(EOT)
