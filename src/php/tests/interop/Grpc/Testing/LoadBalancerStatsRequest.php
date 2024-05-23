<?php
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: src/proto/grpc/testing/messages.proto

namespace Grpc\Testing;

use Google\Protobuf\Internal\GPBType;
use Google\Protobuf\Internal\RepeatedField;
use Google\Protobuf\Internal\GPBUtil;

/**
 * Generated from protobuf message <code>grpc.testing.LoadBalancerStatsRequest</code>
 */
class LoadBalancerStatsRequest extends \Google\Protobuf\Internal\Message
{
    /**
     * Request stats for the next num_rpcs sent by client.
     *
     * Generated from protobuf field <code>int32 num_rpcs = 1;</code>
     */
    protected $num_rpcs = 0;
    /**
     * If num_rpcs have not completed within timeout_sec, return partial results.
     *
     * Generated from protobuf field <code>int32 timeout_sec = 2;</code>
     */
    protected $timeout_sec = 0;
    /**
     * Response header + trailer metadata entries we want the values of.
     * Matching of the keys is case-insensitive as per rfc7540#section-8.1.2
     * * (asterisk) is a special value that will return all metadata entries
     *
     * Generated from protobuf field <code>repeated string metadata_keys = 3;</code>
     */
    private $metadata_keys;

    /**
     * Constructor.
     *
     * @param array $data {
     *     Optional. Data for populating the Message object.
     *
     *     @type int $num_rpcs
     *           Request stats for the next num_rpcs sent by client.
     *     @type int $timeout_sec
     *           If num_rpcs have not completed within timeout_sec, return partial results.
     *     @type array<string>|\Google\Protobuf\Internal\RepeatedField $metadata_keys
     *           Response header + trailer metadata entries we want the values of.
     *           Matching of the keys is case-insensitive as per rfc7540#section-8.1.2
     *           * (asterisk) is a special value that will return all metadata entries
     * }
     */
    public function __construct($data = NULL) {
        \GPBMetadata\Src\Proto\Grpc\Testing\Messages::initOnce();
        parent::__construct($data);
    }

    /**
     * Request stats for the next num_rpcs sent by client.
     *
     * Generated from protobuf field <code>int32 num_rpcs = 1;</code>
     * @return int
     */
    public function getNumRpcs()
    {
        return $this->num_rpcs;
    }

    /**
     * Request stats for the next num_rpcs sent by client.
     *
     * Generated from protobuf field <code>int32 num_rpcs = 1;</code>
     * @param int $var
     * @return $this
     */
    public function setNumRpcs($var)
    {
        GPBUtil::checkInt32($var);
        $this->num_rpcs = $var;

        return $this;
    }

    /**
     * If num_rpcs have not completed within timeout_sec, return partial results.
     *
     * Generated from protobuf field <code>int32 timeout_sec = 2;</code>
     * @return int
     */
    public function getTimeoutSec()
    {
        return $this->timeout_sec;
    }

    /**
     * If num_rpcs have not completed within timeout_sec, return partial results.
     *
     * Generated from protobuf field <code>int32 timeout_sec = 2;</code>
     * @param int $var
     * @return $this
     */
    public function setTimeoutSec($var)
    {
        GPBUtil::checkInt32($var);
        $this->timeout_sec = $var;

        return $this;
    }

    /**
     * Response header + trailer metadata entries we want the values of.
     * Matching of the keys is case-insensitive as per rfc7540#section-8.1.2
     * * (asterisk) is a special value that will return all metadata entries
     *
     * Generated from protobuf field <code>repeated string metadata_keys = 3;</code>
     * @return \Google\Protobuf\Internal\RepeatedField
     */
    public function getMetadataKeys()
    {
        return $this->metadata_keys;
    }

    /**
     * Response header + trailer metadata entries we want the values of.
     * Matching of the keys is case-insensitive as per rfc7540#section-8.1.2
     * * (asterisk) is a special value that will return all metadata entries
     *
     * Generated from protobuf field <code>repeated string metadata_keys = 3;</code>
     * @param array<string>|\Google\Protobuf\Internal\RepeatedField $var
     * @return $this
     */
    public function setMetadataKeys($var)
    {
        $arr = GPBUtil::checkRepeatedField($var, \Google\Protobuf\Internal\GPBType::STRING);
        $this->metadata_keys = $arr;

        return $this;
    }

}

