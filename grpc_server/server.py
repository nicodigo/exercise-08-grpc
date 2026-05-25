# TODO: Implement gRPC server using generated stubs
import grpc
import os
from concurrent import futures
from sqlalchemy.orm import Session
from google.protobuf.timestamp_pb2 import Timestamp

import node_registry_pb2
import node_registry_pb2_grpc
from grpc_server.database import engine, get_db, Base
from grpc_server.models import Node


def node_to_proto(node):
    created = Timestamp()
    created.FromDatetime(node.created_at)
    updated = Timestamp()
    updated.FromDatetime(node.updated_at)

    return node_registry_pb2.NodeResponse(
        id=node.id,
        name=node.name,
        host=node.host,
        port=node.port,
        status=node.status,
        created_at=created,
        updated_at=updated,
    )
class NodeRegistryServicer(node_registry_pb2_grpc.NodeRegistryServicer):

    def Register(self, request, context):
        db: Session = next(get_db())
        existing = db.query(Node).filter(Node.name == request.name).first()
        if existing:
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details("Node already exists")
            return node_registry_pb2.Empty()
        db_node = Node(name=request.name, host=request.host, port=request.port)
        db.add(db_node)
        db.commit()
        db.refresh(db_node)
        return node_to_proto(db_node)


    def List(self, request, context):
        db: Session = next(get_db())
        nodes = db.query(Node).all()
        return  node_registry_pb2.NodeList(nodes=[node_to_proto(node) for node in nodes])


    def Get(self, request, context):
        db: Session = next(get_db())
        node = db.query(Node).filter(Node.name == request.name).first()
        if not(node):
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Node not found")
            return node_registry_pb2.Empty()
        return node_to_proto(node)


    def Delete(self, request, context):
        db: Session = next(get_db())
        node = db.query(Node).filter(Node.name == request.name).first()
        if not(node):
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Node not found")
            return node_registry_pb2.Empty()
        db.delete(node)
        db.commit()
        return  node_registry_pb2.Empty()


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    node_registry_pb2_grpc.add_NodeRegistryServicer_to_server(NodeRegistryServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()
