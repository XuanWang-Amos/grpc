<?php
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: src/proto/grpc/testing/test.proto

namespace GPBMetadata\Src\Proto\Grpc\Testing;

class Test
{
    public static $is_initialized = false;

    public static function initOnce() {
        $pool = \Google\Protobuf\Internal\DescriptorPool::getGeneratedPool();

        if (static::$is_initialized == true) {
          return;
        }
        \GPBMetadata\Src\Proto\Grpc\Testing\PBEmpty::initOnce();
        \GPBMetadata\Src\Proto\Grpc\Testing\Messages::initOnce();
        $pool->internalAddGeneratedFile(
            "\x0A\xD4\x0F\x0A!src/proto/grpc/testing/test.proto\x12\x0Cgrpc.testing\x1A%src/proto/grpc/testing/messages.proto2\xE7\x05\x0A\x0BTestService\x12C\x0A\x09EmptyCall\x12\x1A.grpc.testing.EmptyMessage\x1A\x1A.grpc.testing.EmptyMessage\x12F\x0A\x09UnaryCall\x12\x1B.grpc.testing.SimpleRequest\x1A\x1C.grpc.testing.SimpleResponse\x12O\x0A\x12CacheableUnaryCall\x12\x1B.grpc.testing.SimpleRequest\x1A\x1C.grpc.testing.SimpleResponse\x12l\x0A\x13StreamingOutputCall\x12(.grpc.testing.StreamingOutputCallRequest\x1A).grpc.testing.StreamingOutputCallResponse0\x01\x12i\x0A\x12StreamingInputCall\x12'.grpc.testing.StreamingInputCallRequest\x1A(.grpc.testing.StreamingInputCallResponse(\x01\x12i\x0A\x0EFullDuplexCall\x12(.grpc.testing.StreamingOutputCallRequest\x1A).grpc.testing.StreamingOutputCallResponse(\x010\x01\x12i\x0A\x0EHalfDuplexCall\x12(.grpc.testing.StreamingOutputCallRequest\x1A).grpc.testing.StreamingOutputCallResponse(\x010\x01\x12K\x0A\x11UnimplementedCall\x12\x1A.grpc.testing.EmptyMessage\x1A\x1A.grpc.testing.EmptyMessage2c\x0A\x14UnimplementedService\x12K\x0A\x11UnimplementedCall\x12\x1A.grpc.testing.EmptyMessage\x1A\x1A.grpc.testing.EmptyMessage2\x97\x01\x0A\x10ReconnectService\x12B\x0A\x05Start\x12\x1D.grpc.testing.ReconnectParams\x1A\x1A.grpc.testing.EmptyMessage\x12?\x0A\x04Stop\x12\x1A.grpc.testing.EmptyMessage\x1A\x1B.grpc.testing.ReconnectInfo2\x86\x02\x0A\x18LoadBalancerStatsService\x12c\x0A\x0EGetClientStats\x12&.grpc.testing.LoadBalancerStatsRequest\x1A'.grpc.testing.LoadBalancerStatsResponse\"\x00\x12\x84\x01\x0A\x19GetClientAccumulatedStats\x121.grpc.testing.LoadBalancerAccumulatedStatsRequest\x1A2.grpc.testing.LoadBalancerAccumulatedStatsResponse\"\x002\xEF\x01\x0A\x0BHookService\x12>\x0A\x04Hook\x12\x1A.grpc.testing.EmptyMessage\x1A\x1A.grpc.testing.EmptyMessage\x12S\x0A\x0FSetReturnStatus\x12\$.grpc.testing.SetReturnStatusRequest\x1A\x1A.grpc.testing.EmptyMessage\x12K\x0A\x11ClearReturnStatus\x12\x1A.grpc.testing.EmptyMessage\x1A\x1A.grpc.testing.EmptyMessage2\xF1\x01\x0A\x16XdsUpdateHealthService\x12D\x0A\x0ASetServing\x12\x1A.grpc.testing.EmptyMessage\x1A\x1A.grpc.testing.EmptyMessage\x12G\x0A\x0DSetNotServing\x12\x1A.grpc.testing.EmptyMessage\x1A\x1A.grpc.testing.EmptyMessage\x12H\x0A\x0FSendHookRequest\x12\x19.grpc.testing.HookRequest\x1A\x1A.grpc.testing.HookResponse2{\x0A\x1FXdsUpdateClientConfigureService\x12X\x0A\x09Configure\x12\$.grpc.testing.ClientConfigureRequest\x1A%.grpc.testing.ClientConfigureResponseB\x1D\x0A\x1Bio.grpc.testing.integrationb\x06proto3"
        , true);

        static::$is_initialized = true;
    }
}

