gRPC Observability Example
=====================

The examples here demonstrate how to setup gRPC Python Observability with Opentelemetry.

More details about how to use gRPC Python Observability APIs can be found in [OpenTelemetry Metrics gRFC](https://github.com/grpc/proposal/blob/master/A66-otel-stats.md#opentelemetry-metrics).

### Requirements

The examples here depends on grpcio and grpcio-observability version of 1.62.0 or newer.

### Run the Server

1. Navigate to this directory:

```sh
cd grpc/examples/python/observability
```

2. Run the server:

```sh
python -m observability_greeter_server
```

### Run the Client

Note that client should start within 10 seconds of the server becoming active.

```
python -m observability_greeter_client
```

### Verifying Metrics

On server side, it should print a list of metric names collected:
```
Server started, listening on 50051
Metrics exported on Server side:
grpc.server.call.started
grpc.server.call.sent_total_compressed_message_size
grpc.server.call.rcvd_total_compressed_message_size
grpc.server.call.duration
```

On client side, it should print a list of metric names collected:
```
Greeter client received: Hello You
Metrics exported on client side:
grpc.client.call.duration
grpc.client.attempt.started
grpc.client.attempt.sent_total_compressed_message_size
grpc.client.attempt.rcvd_total_compressed_message_size
grpc.client.attempt.duration
```
