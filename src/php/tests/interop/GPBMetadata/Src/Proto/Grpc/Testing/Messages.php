<?php
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: src/proto/grpc/testing/messages.proto

namespace GPBMetadata\Src\Proto\Grpc\Testing;

class Messages
{
    public static $is_initialized = false;

    public static function initOnce() {
        $pool = \Google\Protobuf\Internal\DescriptorPool::getGeneratedPool();

        if (static::$is_initialized == true) {
          return;
        }
        $pool->internalAddGeneratedFile(
            "\x0A\x80'\x0A%src/proto/grpc/testing/messages.proto\x12\x0Cgrpc.testing\"\x1A\x0A\x09BoolValue\x12\x0D\x0A\x05value\x18\x01 \x01(\x08\"@\x0A\x07Payload\x12'\x0A\x04type\x18\x01 \x01(\x0E2\x19.grpc.testing.PayloadType\x12\x0C\x0A\x04body\x18\x02 \x01(\x0C\"+\x0A\x0AEchoStatus\x12\x0C\x0A\x04code\x18\x01 \x01(\x05\x12\x0F\x0A\x07message\x18\x02 \x01(\x09\"\xC3\x03\x0A\x0DSimpleRequest\x120\x0A\x0Dresponse_type\x18\x01 \x01(\x0E2\x19.grpc.testing.PayloadType\x12\x15\x0A\x0Dresponse_size\x18\x02 \x01(\x05\x12&\x0A\x07payload\x18\x03 \x01(\x0B2\x15.grpc.testing.Payload\x12\x15\x0A\x0Dfill_username\x18\x04 \x01(\x08\x12\x18\x0A\x10fill_oauth_scope\x18\x05 \x01(\x08\x124\x0A\x13response_compressed\x18\x06 \x01(\x0B2\x17.grpc.testing.BoolValue\x121\x0A\x0Fresponse_status\x18\x07 \x01(\x0B2\x18.grpc.testing.EchoStatus\x122\x0A\x11expect_compressed\x18\x08 \x01(\x0B2\x17.grpc.testing.BoolValue\x12\x16\x0A\x0Efill_server_id\x18\x09 \x01(\x08\x12\x1E\x0A\x16fill_grpclb_route_type\x18\x0A \x01(\x08\x12;\x0A\x15orca_per_query_report\x18\x0B \x01(\x0B2\x1C.grpc.testing.TestOrcaReport\"\xBE\x01\x0A\x0ESimpleResponse\x12&\x0A\x07payload\x18\x01 \x01(\x0B2\x15.grpc.testing.Payload\x12\x10\x0A\x08username\x18\x02 \x01(\x09\x12\x13\x0A\x0Boauth_scope\x18\x03 \x01(\x09\x12\x11\x0A\x09server_id\x18\x04 \x01(\x09\x128\x0A\x11grpclb_route_type\x18\x05 \x01(\x0E2\x1D.grpc.testing.GrpclbRouteType\x12\x10\x0A\x08hostname\x18\x06 \x01(\x09\"w\x0A\x19StreamingInputCallRequest\x12&\x0A\x07payload\x18\x01 \x01(\x0B2\x15.grpc.testing.Payload\x122\x0A\x11expect_compressed\x18\x02 \x01(\x0B2\x17.grpc.testing.BoolValue\"=\x0A\x1AStreamingInputCallResponse\x12\x1F\x0A\x17aggregated_payload_size\x18\x01 \x01(\x05\"d\x0A\x12ResponseParameters\x12\x0C\x0A\x04size\x18\x01 \x01(\x05\x12\x13\x0A\x0Binterval_us\x18\x02 \x01(\x05\x12+\x0A\x0Acompressed\x18\x03 \x01(\x0B2\x17.grpc.testing.BoolValue\"\x9F\x02\x0A\x1AStreamingOutputCallRequest\x120\x0A\x0Dresponse_type\x18\x01 \x01(\x0E2\x19.grpc.testing.PayloadType\x12=\x0A\x13response_parameters\x18\x02 \x03(\x0B2 .grpc.testing.ResponseParameters\x12&\x0A\x07payload\x18\x03 \x01(\x0B2\x15.grpc.testing.Payload\x121\x0A\x0Fresponse_status\x18\x07 \x01(\x0B2\x18.grpc.testing.EchoStatus\x125\x0A\x0Forca_oob_report\x18\x08 \x01(\x0B2\x1C.grpc.testing.TestOrcaReport\"E\x0A\x1BStreamingOutputCallResponse\x12&\x0A\x07payload\x18\x01 \x01(\x0B2\x15.grpc.testing.Payload\"3\x0A\x0FReconnectParams\x12 \x0A\x18max_reconnect_backoff_ms\x18\x01 \x01(\x05\"3\x0A\x0DReconnectInfo\x12\x0E\x0A\x06passed\x18\x01 \x01(\x08\x12\x12\x0A\x0Abackoff_ms\x18\x02 \x03(\x05\"X\x0A\x18LoadBalancerStatsRequest\x12\x10\x0A\x08num_rpcs\x18\x01 \x01(\x05\x12\x13\x0A\x0Btimeout_sec\x18\x02 \x01(\x05\x12\x15\x0A\x0Dmetadata_keys\x18\x03 \x03(\x09\"\xB2\x08\x0A\x19LoadBalancerStatsResponse\x12M\x0A\x0Crpcs_by_peer\x18\x01 \x03(\x0B27.grpc.testing.LoadBalancerStatsResponse.RpcsByPeerEntry\x12\x14\x0A\x0Cnum_failures\x18\x02 \x01(\x05\x12Q\x0A\x0Erpcs_by_method\x18\x03 \x03(\x0B29.grpc.testing.LoadBalancerStatsResponse.RpcsByMethodEntry\x12W\x0A\x11metadatas_by_peer\x18\x04 \x03(\x0B2<.grpc.testing.LoadBalancerStatsResponse.MetadatasByPeerEntry\x1Ao\x0A\x0DMetadataEntry\x12\x0B\x0A\x03key\x18\x01 \x01(\x09\x12\x0D\x0A\x05value\x18\x02 \x01(\x09\x12B\x0A\x04type\x18\x03 \x01(\x0E24.grpc.testing.LoadBalancerStatsResponse.MetadataType\x1AV\x0A\x0BRpcMetadata\x12G\x0A\x08metadata\x18\x01 \x03(\x0B25.grpc.testing.LoadBalancerStatsResponse.MetadataEntry\x1A[\x0A\x0EMetadataByPeer\x12I\x0A\x0Crpc_metadata\x18\x01 \x03(\x0B23.grpc.testing.LoadBalancerStatsResponse.RpcMetadata\x1A\x99\x01\x0A\x0ARpcsByPeer\x12X\x0A\x0Crpcs_by_peer\x18\x01 \x03(\x0B2B.grpc.testing.LoadBalancerStatsResponse.RpcsByPeer.RpcsByPeerEntry\x1A1\x0A\x0FRpcsByPeerEntry\x12\x0B\x0A\x03key\x18\x01 \x01(\x09\x12\x0D\x0A\x05value\x18\x02 \x01(\x05:\x028\x01\x1A1\x0A\x0FRpcsByPeerEntry\x12\x0B\x0A\x03key\x18\x01 \x01(\x09\x12\x0D\x0A\x05value\x18\x02 \x01(\x05:\x028\x01\x1Ag\x0A\x11RpcsByMethodEntry\x12\x0B\x0A\x03key\x18\x01 \x01(\x09\x12A\x0A\x05value\x18\x02 \x01(\x0B22.grpc.testing.LoadBalancerStatsResponse.RpcsByPeer:\x028\x01\x1An\x0A\x14MetadatasByPeerEntry\x12\x0B\x0A\x03key\x18\x01 \x01(\x09\x12E\x0A\x05value\x18\x02 \x01(\x0B26.grpc.testing.LoadBalancerStatsResponse.MetadataByPeer:\x028\x01\"6\x0A\x0CMetadataType\x12\x0B\x0A\x07UNKNOWN\x10\x00\x12\x0B\x0A\x07INITIAL\x10\x01\x12\x0C\x0A\x08TRAILING\x10\x02\"%\x0A#LoadBalancerAccumulatedStatsRequest\"\xD8\x07\x0A\$LoadBalancerAccumulatedStatsResponse\x12v\x0A\x1Anum_rpcs_started_by_method\x18\x01 \x03(\x0B2N.grpc.testing.LoadBalancerAccumulatedStatsResponse.NumRpcsStartedByMethodEntryB\x02\x18\x01\x12z\x0A\x1Cnum_rpcs_succeeded_by_method\x18\x02 \x03(\x0B2P.grpc.testing.LoadBalancerAccumulatedStatsResponse.NumRpcsSucceededByMethodEntryB\x02\x18\x01\x12t\x0A\x19num_rpcs_failed_by_method\x18\x03 \x03(\x0B2M.grpc.testing.LoadBalancerAccumulatedStatsResponse.NumRpcsFailedByMethodEntryB\x02\x18\x01\x12`\x0A\x10stats_per_method\x18\x04 \x03(\x0B2F.grpc.testing.LoadBalancerAccumulatedStatsResponse.StatsPerMethodEntry\x1A=\x0A\x1BNumRpcsStartedByMethodEntry\x12\x0B\x0A\x03key\x18\x01 \x01(\x09\x12\x0D\x0A\x05value\x18\x02 \x01(\x05:\x028\x01\x1A?\x0A\x1DNumRpcsSucceededByMethodEntry\x12\x0B\x0A\x03key\x18\x01 \x01(\x09\x12\x0D\x0A\x05value\x18\x02 \x01(\x05:\x028\x01\x1A<\x0A\x1ANumRpcsFailedByMethodEntry\x12\x0B\x0A\x03key\x18\x01 \x01(\x09\x12\x0D\x0A\x05value\x18\x02 \x01(\x05:\x028\x01\x1A\xAE\x01\x0A\x0BMethodStats\x12\x14\x0A\x0Crpcs_started\x18\x01 \x01(\x05\x12Z\x0A\x06result\x18\x02 \x03(\x0B2J.grpc.testing.LoadBalancerAccumulatedStatsResponse.MethodStats.ResultEntry\x1A-\x0A\x0BResultEntry\x12\x0B\x0A\x03key\x18\x01 \x01(\x05\x12\x0D\x0A\x05value\x18\x02 \x01(\x05:\x028\x01\x1Au\x0A\x13StatsPerMethodEntry\x12\x0B\x0A\x03key\x18\x01 \x01(\x09\x12M\x0A\x05value\x18\x02 \x01(\x0B2>.grpc.testing.LoadBalancerAccumulatedStatsResponse.MethodStats:\x028\x01\"\xBA\x02\x0A\x16ClientConfigureRequest\x12;\x0A\x05types\x18\x01 \x03(\x0E2,.grpc.testing.ClientConfigureRequest.RpcType\x12?\x0A\x08metadata\x18\x02 \x03(\x0B2-.grpc.testing.ClientConfigureRequest.Metadata\x12\x13\x0A\x0Btimeout_sec\x18\x03 \x01(\x05\x1Ab\x0A\x08Metadata\x12:\x0A\x04type\x18\x01 \x01(\x0E2,.grpc.testing.ClientConfigureRequest.RpcType\x12\x0B\x0A\x03key\x18\x02 \x01(\x09\x12\x0D\x0A\x05value\x18\x03 \x01(\x09\")\x0A\x07RpcType\x12\x0E\x0A\x0AEMPTY_CALL\x10\x00\x12\x0E\x0A\x0AUNARY_CALL\x10\x01\"\x19\x0A\x17ClientConfigureResponse\"\x19\x0A\x0AMemorySize\x12\x0B\x0A\x03rss\x18\x01 \x01(\x03\"\xB6\x02\x0A\x0ETestOrcaReport\x12\x17\x0A\x0Fcpu_utilization\x18\x01 \x01(\x01\x12\x1A\x0A\x12memory_utilization\x18\x02 \x01(\x01\x12C\x0A\x0Crequest_cost\x18\x03 \x03(\x0B2-.grpc.testing.TestOrcaReport.RequestCostEntry\x12B\x0A\x0Butilization\x18\x04 \x03(\x0B2-.grpc.testing.TestOrcaReport.UtilizationEntry\x1A2\x0A\x10RequestCostEntry\x12\x0B\x0A\x03key\x18\x01 \x01(\x09\x12\x0D\x0A\x05value\x18\x02 \x01(\x01:\x028\x01\x1A2\x0A\x10UtilizationEntry\x12\x0B\x0A\x03key\x18\x01 \x01(\x09\x12\x0D\x0A\x05value\x18\x02 \x01(\x01:\x028\x01\"V\x0A\x16SetReturnStatusRequest\x12\x1B\x0A\x13grpc_code_to_return\x18\x01 \x01(\x05\x12\x1F\x0A\x17grpc_status_description\x18\x02 \x01(\x09\"\xE7\x01\x0A\x0BHookRequest\x12=\x0A\x07command\x18\x01 \x01(\x0E2,.grpc.testing.HookRequest.HookRequestCommand\x12\x1B\x0A\x13grpc_code_to_return\x18\x02 \x01(\x05\x12\x1F\x0A\x17grpc_status_description\x18\x03 \x01(\x09\x12\x13\x0A\x0Bserver_port\x18\x04 \x01(\x05\"F\x0A\x12HookRequestCommand\x12\x0F\x0A\x0BUNSPECIFIED\x10\x00\x12\x09\x0A\x05START\x10\x01\x12\x08\x0A\x04STOP\x10\x02\x12\x0A\x0A\x06RETURN\x10\x03\"\x0E\x0A\x0CHookResponse*\x1F\x0A\x0BPayloadType\x12\x10\x0A\x0CCOMPRESSABLE\x10\x00*o\x0A\x0FGrpclbRouteType\x12\x1D\x0A\x19GRPCLB_ROUTE_TYPE_UNKNOWN\x10\x00\x12\x1E\x0A\x1AGRPCLB_ROUTE_TYPE_FALLBACK\x10\x01\x12\x1D\x0A\x19GRPCLB_ROUTE_TYPE_BACKEND\x10\x02B\x1D\x0A\x1Bio.grpc.testing.integrationb\x06proto3"
        , true);

        static::$is_initialized = true;
    }
}

