from mikrotik_utils import test_connection, create_queue, delete_queue, block_ip, unblock_ip

if __name__ == "__main__":
    ok, msg = test_connection()
    print("Conexión OK?:", ok)
    print("Respuesta:", msg)
    # Ejemplos (ajusta IP y datos):
    # print(create_queue(ip="192.168.1.100", up_kbps=2048, down_kbps=10240, numero_cliente=1234, nombre_cliente="Juan Perez"))
    # print(block_ip("192.168.1.100", numero_cliente=1234))
    # print(unblock_ip("192.168.1.100"))