<?php
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: src/proto/grpc/testing/messages.proto

namespace Grpc\Testing;

use Google\Protobuf\Internal\GPBType;
use Google\Protobuf\Internal\RepeatedField;
use Google\Protobuf\Internal\GPBUtil;

/**
 * Unary response, as configured by the request.
 *
 * Generated from protobuf message <code>grpc.testing.SimpleResponse</code>
 */
class SimpleResponse extends \Google\Protobuf\Internal\Message
{
    /**
     * Payload to increase message size.
     *
     * Generated from protobuf field <code>.grpc.testing.Payload payload = 1;</code>
     */
    protected $payload = null;
    /**
     * The user the request came from, for verifying authentication was
     * successful when the client expected it.
     *
     * Generated from protobuf field <code>string username = 2;</code>
     */
    protected $username = '';
    /**
     * OAuth scope.
     *
     * Generated from protobuf field <code>string oauth_scope = 3;</code>
     */
    protected $oauth_scope = '';
    /**
     * Server ID. This must be unique among different server instances,
     * but the same across all RPC's made to a particular server instance.
     *
     * Generated from protobuf field <code>string server_id = 4;</code>
     */
    protected $server_id = '';
    /**
     * gRPCLB Path.
     *
     * Generated from protobuf field <code>.grpc.testing.GrpclbRouteType grpclb_route_type = 5;</code>
     */
    protected $grpclb_route_type = 0;
    /**
     * Server hostname.
     *
     * Generated from protobuf field <code>string hostname = 6;</code>
     */
    protected $hostname = '';

    /**
     * Constructor.
     *
     * @param array $data {
     *     Optional. Data for populating the Message object.
     *
     *     @type \Grpc\Testing\Payload $payload
     *           Payload to increase message size.
     *     @type string $username
     *           The user the request came from, for verifying authentication was
     *           successful when the client expected it.
     *     @type string $oauth_scope
     *           OAuth scope.
     *     @type string $server_id
     *           Server ID. This must be unique among different server instances,
     *           but the same across all RPC's made to a particular server instance.
     *     @type int $grpclb_route_type
     *           gRPCLB Path.
     *     @type string $hostname
     *           Server hostname.
     * }
     */
    public function __construct($data = NULL) {
        \GPBMetadata\Src\Proto\Grpc\Testing\Messages::initOnce();
        parent::__construct($data);
    }

    /**
     * Payload to increase message size.
     *
     * Generated from protobuf field <code>.grpc.testing.Payload payload = 1;</code>
     * @return \Grpc\Testing\Payload|null
     */
    public function getPayload()
    {
        return $this->payload;
    }

    public function hasPayload()
    {
        return isset($this->payload);
    }

    public function clearPayload()
    {
        unset($this->payload);
    }

    /**
     * Payload to increase message size.
     *
     * Generated from protobuf field <code>.grpc.testing.Payload payload = 1;</code>
     * @param \Grpc\Testing\Payload $var
     * @return $this
     */
    public function setPayload($var)
    {
        GPBUtil::checkMessage($var, \Grpc\Testing\Payload::class);
        $this->payload = $var;

        return $this;
    }

    /**
     * The user the request came from, for verifying authentication was
     * successful when the client expected it.
     *
     * Generated from protobuf field <code>string username = 2;</code>
     * @return string
     */
    public function getUsername()
    {
        return $this->username;
    }

    /**
     * The user the request came from, for verifying authentication was
     * successful when the client expected it.
     *
     * Generated from protobuf field <code>string username = 2;</code>
     * @param string $var
     * @return $this
     */
    public function setUsername($var)
    {
        GPBUtil::checkString($var, True);
        $this->username = $var;

        return $this;
    }

    /**
     * OAuth scope.
     *
     * Generated from protobuf field <code>string oauth_scope = 3;</code>
     * @return string
     */
    public function getOauthScope()
    {
        return $this->oauth_scope;
    }

    /**
     * OAuth scope.
     *
     * Generated from protobuf field <code>string oauth_scope = 3;</code>
     * @param string $var
     * @return $this
     */
    public function setOauthScope($var)
    {
        GPBUtil::checkString($var, True);
        $this->oauth_scope = $var;

        return $this;
    }

    /**
     * Server ID. This must be unique among different server instances,
     * but the same across all RPC's made to a particular server instance.
     *
     * Generated from protobuf field <code>string server_id = 4;</code>
     * @return string
     */
    public function getServerId()
    {
        return $this->server_id;
    }

    /**
     * Server ID. This must be unique among different server instances,
     * but the same across all RPC's made to a particular server instance.
     *
     * Generated from protobuf field <code>string server_id = 4;</code>
     * @param string $var
     * @return $this
     */
    public function setServerId($var)
    {
        GPBUtil::checkString($var, True);
        $this->server_id = $var;

        return $this;
    }

    /**
     * gRPCLB Path.
     *
     * Generated from protobuf field <code>.grpc.testing.GrpclbRouteType grpclb_route_type = 5;</code>
     * @return int
     */
    public function getGrpclbRouteType()
    {
        return $this->grpclb_route_type;
    }

    /**
     * gRPCLB Path.
     *
     * Generated from protobuf field <code>.grpc.testing.GrpclbRouteType grpclb_route_type = 5;</code>
     * @param int $var
     * @return $this
     */
    public function setGrpclbRouteType($var)
    {
        GPBUtil::checkEnum($var, \Grpc\Testing\GrpclbRouteType::class);
        $this->grpclb_route_type = $var;

        return $this;
    }

    /**
     * Server hostname.
     *
     * Generated from protobuf field <code>string hostname = 6;</code>
     * @return string
     */
    public function getHostname()
    {
        return $this->hostname;
    }

    /**
     * Server hostname.
     *
     * Generated from protobuf field <code>string hostname = 6;</code>
     * @param string $var
     * @return $this
     */
    public function setHostname($var)
    {
        GPBUtil::checkString($var, True);
        $this->hostname = $var;

        return $this;
    }

}

