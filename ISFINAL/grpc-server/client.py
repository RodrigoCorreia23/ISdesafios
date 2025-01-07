import grpc
import server_services_pb2
import server_services_pb2_grpc



def get_states(client_stub, country_name):
    request = server_services_pb2.CountryRequest(country=country_name)
    response = client_stub.GetStatesByCountry(request)
    print(f"Estados encontrados para {country_name}:")
    for state in response.states:
        print(state)


def run_client():
    channel = grpc.insecure_channel(
        "localhost:50051",
        options=[
            ('grpc.max_receive_message_length', 50 * 1024 * 1024),  # 50 MB
            ('grpc.max_send_message_length', 50 * 1024 * 1024),  # 50 MB
        ]
    )
    stub = server_services_pb2_grpc.FileServiceStub(channel)

    # Enviar o arquivo CSV
    with open("Sales.csv", "rb") as f:
        csv_data = f.read()

    request = server_services_pb2.CSVRequest(file=csv_data)
    response = stub.ProcessCSV(request)
    print("Validação do XML:", response.valid_xml)

    # Solicitar o nome do país ao usuário
    country_name = input("Digite o nome do país para procurar os estados: ").strip()
    get_states(stub, country_name)







if __name__ == "__main__":
    run_client()
