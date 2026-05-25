# TODO: FastAPI gateway that translates REST -> gRPC calls
import grpc
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from google.protobuf.json_format import MessageToDict
import node_registry_pb2
import node_registry_pb2_grpc

# Conexión al server gRPC
channel = grpc.insecure_channel("grpc-server:50051")
stub = node_registry_pb2_grpc.NodeRegistryStub(channel)

app = FastAPI()

# Schema de entrada para POST
class NodeCreate(BaseModel):
    name: str
    host: str
    port: int

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/nodes", status_code=201)
def register_node(node: NodeCreate):
    # 1. construir RegisterRequest con los campos de node
    # 2. llamar stub.Register dentro de try/except grpc.RpcError
    # 3. convertir respuesta con MessageToDict y devolver
    request = node_registry_pb2.RegisterRequest(
        name=node.name,
        host=node.host,
        port=node.port,
    )
    try:
        response = stub.Register(request)
        return MessageToDict(response, preserving_proto_field_name=True)
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.ALREADY_EXISTS:
            raise HTTPException(status_code=409)

@app.get("/api/nodes")
def list_nodes():
    # 1. llamar stub.List(node_registry_pb2.Empty())
    # 2. el resultado tiene .nodes — es una lista de NodeResponse proto
    # 3. convertir cada uno con MessageToDict y devolver lista
    request = node_registry_pb2.Empty()
    response = stub.List(request)
    return [MessageToDict(node, preserving_proto_field_name=True) for node in response.nodes]


@app.get("/api/nodes/{name}")
def get_node(name: str):
    # 1. construir GetRequest(name=name)
    # 2. llamar stub.Get dentro de try/except
    # 3. convertir y devolver
    request = node_registry_pb2.GetRequest(
        name=name,
    )
    try:
        response = stub.Get(request)
        return MessageToDict(response, preserving_proto_field_name=True)
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(status_code=404)

@app.delete("/api/nodes/{name}")
def delete_node(name: str):
    # 1. construir DeleteRequest(name=name)
    # 2. llamar stub.Delete dentro de try/except
    # 3. devolver 204 — Response(status_code=204)
    request = node_registry_pb2.DeleteRequest(
        name=name,
    )
    try:
        response = stub.Delete(request)
        return Response(status_code=204)
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(status_code=404)
