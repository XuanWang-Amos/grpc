<?php
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: src/proto/grpc/testing/messages.proto

namespace Grpc\Testing\LoadBalancerStatsResponse;

use Google\Protobuf\Internal\GPBType;
use Google\Protobuf\Internal\RepeatedField;
use Google\Protobuf\Internal\GPBUtil;

/**
 * Generated from protobuf message <code>grpc.testing.LoadBalancerStatsResponse.RpcsByPeer</code>
 */
class RpcsByPeer extends \Google\Protobuf\Internal\Message
{
    /**
     * The number of completed RPCs for each peer.
     *
     * Generated from protobuf field <code>map<string, int32> rpcs_by_peer = 1;</code>
     */
    private $rpcs_by_peer;

    /**
     * Constructor.
     *
     * @param array $data {
     *     Optional. Data for populating the Message object.
     *
     *     @type array|\Google\Protobuf\Internal\MapField $rpcs_by_peer
     *           The number of completed RPCs for each peer.
     * }
     */
    public function __construct($data = NULL) {
        \GPBMetadata\Src\Proto\Grpc\Testing\Messages::initOnce();
        parent::__construct($data);
    }

    /**
     * The number of completed RPCs for each peer.
     *
     * Generated from protobuf field <code>map<string, int32> rpcs_by_peer = 1;</code>
     * @return \Google\Protobuf\Internal\MapField
     */
    public function getRpcsByPeer()
    {
        return $this->rpcs_by_peer;
    }

    /**
     * The number of completed RPCs for each peer.
     *
     * Generated from protobuf field <code>map<string, int32> rpcs_by_peer = 1;</code>
     * @param array|\Google\Protobuf\Internal\MapField $var
     * @return $this
     */
    public function setRpcsByPeer($var)
    {
        $arr = GPBUtil::checkMapField($var, \Google\Protobuf\Internal\GPBType::STRING, \Google\Protobuf\Internal\GPBType::INT32);
        $this->rpcs_by_peer = $arr;

        return $this;
    }

}

