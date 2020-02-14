import grpc
import relic_pb2
import relic_pb2_grpc
from concurrent import futures
import time

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

grpc_port = '[::]:50051'

def get_sql():
    with open("relicdb.sqlite3", 'rb') as fd:
        contents = fd.read()
    return contents

class DataSenderServicer(relic_pb2_grpc.DataSenderServicer):

    def send_data(self, request, context):
        sql = get_sql()
        return relic_pb2.MyData(data=sql)
        
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    relic_pb2_grpc.add_DataSenderServicer_to_server(DataSenderServicer(), server)
    server.add_insecure_port(grpc_port)
    server.start()
    print("Server started !")
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
