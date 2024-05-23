<?php
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: src/proto/grpc/testing/messages.proto

namespace Grpc\Testing\ClientConfigureRequest;

use UnexpectedValueException;

/**
 * Type of RPCs to send.
 *
 * Protobuf type <code>grpc.testing.ClientConfigureRequest.RpcType</code>
 */
class RpcType
{
    /**
     * Generated from protobuf enum <code>EMPTY_CALL = 0;</code>
     */
    const EMPTY_CALL = 0;
    /**
     * Generated from protobuf enum <code>UNARY_CALL = 1;</code>
     */
    const UNARY_CALL = 1;

    private static $valueToName = [
        self::EMPTY_CALL => 'EMPTY_CALL',
        self::UNARY_CALL => 'UNARY_CALL',
    ];

    public static function name($value)
    {
        if (!isset(self::$valueToName[$value])) {
            throw new UnexpectedValueException(sprintf(
                    'Enum %s has no name defined for value %s', __CLASS__, $value));
        }
        return self::$valueToName[$value];
    }


    public static function value($name)
    {
        $const = __CLASS__ . '::' . strtoupper($name);
        if (!defined($const)) {
            throw new UnexpectedValueException(sprintf(
                    'Enum %s has no value defined for name %s', __CLASS__, $name));
        }
        return constant($const);
    }
}

