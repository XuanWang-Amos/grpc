/* This file was generated by upb_generator from the input file:
 *
 *     envoy/config/core/v3/address.proto
 *
 * Do not edit -- your changes will be discarded when the file is
 * regenerated.
 * NO CHECKED-IN PROTOBUF GENCODE */


#include "upb/reflection/def.h"
#include "envoy/config/core/v3/address.upbdefs.h"
#include "envoy/config/core/v3/address.upb_minitable.h"

extern _upb_DefPool_Init envoy_config_core_v3_extension_proto_upbdefinit;
extern _upb_DefPool_Init envoy_config_core_v3_socket_option_proto_upbdefinit;
extern _upb_DefPool_Init google_protobuf_wrappers_proto_upbdefinit;
extern _upb_DefPool_Init envoy_annotations_deprecation_proto_upbdefinit;
extern _upb_DefPool_Init udpa_annotations_status_proto_upbdefinit;
extern _upb_DefPool_Init udpa_annotations_versioning_proto_upbdefinit;
extern _upb_DefPool_Init validate_validate_proto_upbdefinit;

static const char descriptor[2534] = {
    '\n', '\"', 'e', 'n', 'v', 'o', 'y', '/', 'c', 'o', 'n', 'f',
    'i', 'g', '/', 'c', 'o', 'r', 'e', '/', 'v', '3', '/', 'a',
    'd', 'd', 'r', 'e', 's', 's', '.', 'p', 'r', 'o', 't', 'o',
    '\022', '\024', 'e', 'n', 'v', 'o', 'y', '.', 'c', 'o', 'n', 'f',
    'i', 'g', '.', 'c', 'o', 'r', 'e', '.', 'v', '3', '\032', '$',
    'e', 'n', 'v', 'o', 'y', '/', 'c', 'o', 'n', 'f', 'i', 'g',
    '/', 'c', 'o', 'r', 'e', '/', 'v', '3', '/', 'e', 'x', 't',
    'e', 'n', 's', 'i', 'o', 'n', '.', 'p', 'r', 'o', 't', 'o',
    '\032', '(', 'e', 'n', 'v', 'o', 'y', '/', 'c', 'o', 'n', 'f',
    'i', 'g', '/', 'c', 'o', 'r', 'e', '/', 'v', '3', '/', 's',
    'o', 'c', 'k', 'e', 't', '_', 'o', 'p', 't', 'i', 'o', 'n',
    '.', 'p', 'r', 'o', 't', 'o', '\032', '\036', 'g', 'o', 'o', 'g',
    'l', 'e', '/', 'p', 'r', 'o', 't', 'o', 'b', 'u', 'f', '/',
    'w', 'r', 'a', 'p', 'p', 'e', 'r', 's', '.', 'p', 'r', 'o',
    't', 'o', '\032', '#', 'e', 'n', 'v', 'o', 'y', '/', 'a', 'n',
    'n', 'o', 't', 'a', 't', 'i', 'o', 'n', 's', '/', 'd', 'e',
    'p', 'r', 'e', 'c', 'a', 't', 'i', 'o', 'n', '.', 'p', 'r',
    'o', 't', 'o', '\032', '\035', 'u', 'd', 'p', 'a', '/', 'a', 'n',
    'n', 'o', 't', 'a', 't', 'i', 'o', 'n', 's', '/', 's', 't',
    'a', 't', 'u', 's', '.', 'p', 'r', 'o', 't', 'o', '\032', '!',
    'u', 'd', 'p', 'a', '/', 'a', 'n', 'n', 'o', 't', 'a', 't',
    'i', 'o', 'n', 's', '/', 'v', 'e', 'r', 's', 'i', 'o', 'n',
    'i', 'n', 'g', '.', 'p', 'r', 'o', 't', 'o', '\032', '\027', 'v',
    'a', 'l', 'i', 'd', 'a', 't', 'e', '/', 'v', 'a', 'l', 'i',
    'd', 'a', 't', 'e', '.', 'p', 'r', 'o', 't', 'o', '\"', '`',
    '\n', '\004', 'P', 'i', 'p', 'e', '\022', '\033', '\n', '\004', 'p', 'a',
    't', 'h', '\030', '\001', ' ', '\001', '(', '\t', 'B', '\007', '\372', 'B',
    '\004', 'r', '\002', '\020', '\001', 'R', '\004', 'p', 'a', 't', 'h', '\022',
    '\034', '\n', '\004', 'm', 'o', 'd', 'e', '\030', '\002', ' ', '\001', '(',
    '\r', 'B', '\010', '\372', 'B', '\005', '*', '\003', '\030', '\377', '\003', 'R',
    '\004', 'm', 'o', 'd', 'e', ':', '\035', '\232', '\305', '\210', '\036', '\030',
    '\n', '\026', 'e', 'n', 'v', 'o', 'y', '.', 'a', 'p', 'i', '.',
    'v', '2', '.', 'c', 'o', 'r', 'e', '.', 'P', 'i', 'p', 'e',
    '\"', '\212', '\001', '\n', '\024', 'E', 'n', 'v', 'o', 'y', 'I', 'n',
    't', 'e', 'r', 'n', 'a', 'l', 'A', 'd', 'd', 'r', 'e', 's',
    's', '\022', '2', '\n', '\024', 's', 'e', 'r', 'v', 'e', 'r', '_',
    'l', 'i', 's', 't', 'e', 'n', 'e', 'r', '_', 'n', 'a', 'm',
    'e', '\030', '\001', ' ', '\001', '(', '\t', 'H', '\000', 'R', '\022', 's',
    'e', 'r', 'v', 'e', 'r', 'L', 'i', 's', 't', 'e', 'n', 'e',
    'r', 'N', 'a', 'm', 'e', '\022', '\037', '\n', '\013', 'e', 'n', 'd',
    'p', 'o', 'i', 'n', 't', '_', 'i', 'd', '\030', '\002', ' ', '\001',
    '(', '\t', 'R', '\n', 'e', 'n', 'd', 'p', 'o', 'i', 'n', 't',
    'I', 'd', 'B', '\035', '\n', '\026', 'a', 'd', 'd', 'r', 'e', 's',
    's', '_', 'n', 'a', 'm', 'e', '_', 's', 'p', 'e', 'c', 'i',
    'f', 'i', 'e', 'r', '\022', '\003', '\370', 'B', '\001', '\"', '\366', '\002',
    '\n', '\r', 'S', 'o', 'c', 'k', 'e', 't', 'A', 'd', 'd', 'r',
    'e', 's', 's', '\022', 'R', '\n', '\010', 'p', 'r', 'o', 't', 'o',
    'c', 'o', 'l', '\030', '\001', ' ', '\001', '(', '\016', '2', ',', '.',
    'e', 'n', 'v', 'o', 'y', '.', 'c', 'o', 'n', 'f', 'i', 'g',
    '.', 'c', 'o', 'r', 'e', '.', 'v', '3', '.', 'S', 'o', 'c',
    'k', 'e', 't', 'A', 'd', 'd', 'r', 'e', 's', 's', '.', 'P',
    'r', 'o', 't', 'o', 'c', 'o', 'l', 'B', '\010', '\372', 'B', '\005',
    '\202', '\001', '\002', '\020', '\001', 'R', '\010', 'p', 'r', 'o', 't', 'o',
    'c', 'o', 'l', '\022', '!', '\n', '\007', 'a', 'd', 'd', 'r', 'e',
    's', 's', '\030', '\002', ' ', '\001', '(', '\t', 'B', '\007', '\372', 'B',
    '\004', 'r', '\002', '\020', '\001', 'R', '\007', 'a', 'd', 'd', 'r', 'e',
    's', 's', '\022', '*', '\n', '\n', 'p', 'o', 'r', 't', '_', 'v',
    'a', 'l', 'u', 'e', '\030', '\003', ' ', '\001', '(', '\r', 'B', '\t',
    '\372', 'B', '\006', '*', '\004', '\030', '\377', '\377', '\003', 'H', '\000', 'R',
    '\t', 'p', 'o', 'r', 't', 'V', 'a', 'l', 'u', 'e', '\022', '\037',
    '\n', '\n', 'n', 'a', 'm', 'e', 'd', '_', 'p', 'o', 'r', 't',
    '\030', '\004', ' ', '\001', '(', '\t', 'H', '\000', 'R', '\t', 'n', 'a',
    'm', 'e', 'd', 'P', 'o', 'r', 't', '\022', '#', '\n', '\r', 'r',
    'e', 's', 'o', 'l', 'v', 'e', 'r', '_', 'n', 'a', 'm', 'e',
    '\030', '\005', ' ', '\001', '(', '\t', 'R', '\014', 'r', 'e', 's', 'o',
    'l', 'v', 'e', 'r', 'N', 'a', 'm', 'e', '\022', '\037', '\n', '\013',
    'i', 'p', 'v', '4', '_', 'c', 'o', 'm', 'p', 'a', 't', '\030',
    '\006', ' ', '\001', '(', '\010', 'R', '\n', 'i', 'p', 'v', '4', 'C',
    'o', 'm', 'p', 'a', 't', '\"', '\034', '\n', '\010', 'P', 'r', 'o',
    't', 'o', 'c', 'o', 'l', '\022', '\007', '\n', '\003', 'T', 'C', 'P',
    '\020', '\000', '\022', '\007', '\n', '\003', 'U', 'D', 'P', '\020', '\001', ':',
    '&', '\232', '\305', '\210', '\036', '!', '\n', '\037', 'e', 'n', 'v', 'o',
    'y', '.', 'a', 'p', 'i', '.', 'v', '2', '.', 'c', 'o', 'r',
    'e', '.', 'S', 'o', 'c', 'k', 'e', 't', 'A', 'd', 'd', 'r',
    'e', 's', 's', 'B', '\025', '\n', '\016', 'p', 'o', 'r', 't', '_',
    's', 'p', 'e', 'c', 'i', 'f', 'i', 'e', 'r', '\022', '\003', '\370',
    'B', '\001', '\"', '\220', '\002', '\n', '\014', 'T', 'c', 'p', 'K', 'e',
    'e', 'p', 'a', 'l', 'i', 'v', 'e', '\022', 'G', '\n', '\020', 'k',
    'e', 'e', 'p', 'a', 'l', 'i', 'v', 'e', '_', 'p', 'r', 'o',
    'b', 'e', 's', '\030', '\001', ' ', '\001', '(', '\013', '2', '\034', '.',
    'g', 'o', 'o', 'g', 'l', 'e', '.', 'p', 'r', 'o', 't', 'o',
    'b', 'u', 'f', '.', 'U', 'I', 'n', 't', '3', '2', 'V', 'a',
    'l', 'u', 'e', 'R', '\017', 'k', 'e', 'e', 'p', 'a', 'l', 'i',
    'v', 'e', 'P', 'r', 'o', 'b', 'e', 's', '\022', 'C', '\n', '\016',
    'k', 'e', 'e', 'p', 'a', 'l', 'i', 'v', 'e', '_', 't', 'i',
    'm', 'e', '\030', '\002', ' ', '\001', '(', '\013', '2', '\034', '.', 'g',
    'o', 'o', 'g', 'l', 'e', '.', 'p', 'r', 'o', 't', 'o', 'b',
    'u', 'f', '.', 'U', 'I', 'n', 't', '3', '2', 'V', 'a', 'l',
    'u', 'e', 'R', '\r', 'k', 'e', 'e', 'p', 'a', 'l', 'i', 'v',
    'e', 'T', 'i', 'm', 'e', '\022', 'K', '\n', '\022', 'k', 'e', 'e',
    'p', 'a', 'l', 'i', 'v', 'e', '_', 'i', 'n', 't', 'e', 'r',
    'v', 'a', 'l', '\030', '\003', ' ', '\001', '(', '\013', '2', '\034', '.',
    'g', 'o', 'o', 'g', 'l', 'e', '.', 'p', 'r', 'o', 't', 'o',
    'b', 'u', 'f', '.', 'U', 'I', 'n', 't', '3', '2', 'V', 'a',
    'l', 'u', 'e', 'R', '\021', 'k', 'e', 'e', 'p', 'a', 'l', 'i',
    'v', 'e', 'I', 'n', 't', 'e', 'r', 'v', 'a', 'l', ':', '%',
    '\232', '\305', '\210', '\036', ' ', '\n', '\036', 'e', 'n', 'v', 'o', 'y',
    '.', 'a', 'p', 'i', '.', 'v', '2', '.', 'c', 'o', 'r', 'e',
    '.', 'T', 'c', 'p', 'K', 'e', 'e', 'p', 'a', 'l', 'i', 'v',
    'e', '\"', '\261', '\001', '\n', '\022', 'E', 'x', 't', 'r', 'a', 'S',
    'o', 'u', 'r', 'c', 'e', 'A', 'd', 'd', 'r', 'e', 's', 's',
    '\022', 'G', '\n', '\007', 'a', 'd', 'd', 'r', 'e', 's', 's', '\030',
    '\001', ' ', '\001', '(', '\013', '2', '#', '.', 'e', 'n', 'v', 'o',
    'y', '.', 'c', 'o', 'n', 'f', 'i', 'g', '.', 'c', 'o', 'r',
    'e', '.', 'v', '3', '.', 'S', 'o', 'c', 'k', 'e', 't', 'A',
    'd', 'd', 'r', 'e', 's', 's', 'B', '\010', '\372', 'B', '\005', '\212',
    '\001', '\002', '\020', '\001', 'R', '\007', 'a', 'd', 'd', 'r', 'e', 's',
    's', '\022', 'R', '\n', '\016', 's', 'o', 'c', 'k', 'e', 't', '_',
    'o', 'p', 't', 'i', 'o', 'n', 's', '\030', '\002', ' ', '\001', '(',
    '\013', '2', '+', '.', 'e', 'n', 'v', 'o', 'y', '.', 'c', 'o',
    'n', 'f', 'i', 'g', '.', 'c', 'o', 'r', 'e', '.', 'v', '3',
    '.', 'S', 'o', 'c', 'k', 'e', 't', 'O', 'p', 't', 'i', 'o',
    'n', 's', 'O', 'v', 'e', 'r', 'r', 'i', 'd', 'e', 'R', '\r',
    's', 'o', 'c', 'k', 'e', 't', 'O', 'p', 't', 'i', 'o', 'n',
    's', '\"', '\264', '\004', '\n', '\n', 'B', 'i', 'n', 'd', 'C', 'o',
    'n', 'f', 'i', 'g', '\022', 'J', '\n', '\016', 's', 'o', 'u', 'r',
    'c', 'e', '_', 'a', 'd', 'd', 'r', 'e', 's', 's', '\030', '\001',
    ' ', '\001', '(', '\013', '2', '#', '.', 'e', 'n', 'v', 'o', 'y',
    '.', 'c', 'o', 'n', 'f', 'i', 'g', '.', 'c', 'o', 'r', 'e',
    '.', 'v', '3', '.', 'S', 'o', 'c', 'k', 'e', 't', 'A', 'd',
    'd', 'r', 'e', 's', 's', 'R', '\r', 's', 'o', 'u', 'r', 'c',
    'e', 'A', 'd', 'd', 'r', 'e', 's', 's', '\022', '6', '\n', '\010',
    'f', 'r', 'e', 'e', 'b', 'i', 'n', 'd', '\030', '\002', ' ', '\001',
    '(', '\013', '2', '\032', '.', 'g', 'o', 'o', 'g', 'l', 'e', '.',
    'p', 'r', 'o', 't', 'o', 'b', 'u', 'f', '.', 'B', 'o', 'o',
    'l', 'V', 'a', 'l', 'u', 'e', 'R', '\010', 'f', 'r', 'e', 'e',
    'b', 'i', 'n', 'd', '\022', 'I', '\n', '\016', 's', 'o', 'c', 'k',
    'e', 't', '_', 'o', 'p', 't', 'i', 'o', 'n', 's', '\030', '\003',
    ' ', '\003', '(', '\013', '2', '\"', '.', 'e', 'n', 'v', 'o', 'y',
    '.', 'c', 'o', 'n', 'f', 'i', 'g', '.', 'c', 'o', 'r', 'e',
    '.', 'v', '3', '.', 'S', 'o', 'c', 'k', 'e', 't', 'O', 'p',
    't', 'i', 'o', 'n', 'R', '\r', 's', 'o', 'c', 'k', 'e', 't',
    'O', 'p', 't', 'i', 'o', 'n', 's', '\022', '^', '\n', '\026', 'e',
    'x', 't', 'r', 'a', '_', 's', 'o', 'u', 'r', 'c', 'e', '_',
    'a', 'd', 'd', 'r', 'e', 's', 's', 'e', 's', '\030', '\005', ' ',
    '\003', '(', '\013', '2', '(', '.', 'e', 'n', 'v', 'o', 'y', '.',
    'c', 'o', 'n', 'f', 'i', 'g', '.', 'c', 'o', 'r', 'e', '.',
    'v', '3', '.', 'E', 'x', 't', 'r', 'a', 'S', 'o', 'u', 'r',
    'c', 'e', 'A', 'd', 'd', 'r', 'e', 's', 's', 'R', '\024', 'e',
    'x', 't', 'r', 'a', 'S', 'o', 'u', 'r', 'c', 'e', 'A', 'd',
    'd', 'r', 'e', 's', 's', 'e', 's', '\022', 'p', '\n', '\033', 'a',
    'd', 'd', 'i', 't', 'i', 'o', 'n', 'a', 'l', '_', 's', 'o',
    'u', 'r', 'c', 'e', '_', 'a', 'd', 'd', 'r', 'e', 's', 's',
    'e', 's', '\030', '\004', ' ', '\003', '(', '\013', '2', '#', '.', 'e',
    'n', 'v', 'o', 'y', '.', 'c', 'o', 'n', 'f', 'i', 'g', '.',
    'c', 'o', 'r', 'e', '.', 'v', '3', '.', 'S', 'o', 'c', 'k',
    'e', 't', 'A', 'd', 'd', 'r', 'e', 's', 's', 'B', '\013', '\030',
    '\001', '\222', '\307', '\206', '\330', '\004', '\003', '3', '.', '0', 'R', '\031',
    'a', 'd', 'd', 'i', 't', 'i', 'o', 'n', 'a', 'l', 'S', 'o',
    'u', 'r', 'c', 'e', 'A', 'd', 'd', 'r', 'e', 's', 's', 'e',
    's', '\022', '`', '\n', '\026', 'l', 'o', 'c', 'a', 'l', '_', 'a',
    'd', 'd', 'r', 'e', 's', 's', '_', 's', 'e', 'l', 'e', 'c',
    't', 'o', 'r', '\030', '\006', ' ', '\001', '(', '\013', '2', '*', '.',
    'e', 'n', 'v', 'o', 'y', '.', 'c', 'o', 'n', 'f', 'i', 'g',
    '.', 'c', 'o', 'r', 'e', '.', 'v', '3', '.', 'T', 'y', 'p',
    'e', 'd', 'E', 'x', 't', 'e', 'n', 's', 'i', 'o', 'n', 'C',
    'o', 'n', 'f', 'i', 'g', 'R', '\024', 'l', 'o', 'c', 'a', 'l',
    'A', 'd', 'd', 'r', 'e', 's', 's', 'S', 'e', 'l', 'e', 'c',
    't', 'o', 'r', ':', '#', '\232', '\305', '\210', '\036', '\036', '\n', '\034',
    'e', 'n', 'v', 'o', 'y', '.', 'a', 'p', 'i', '.', 'v', '2',
    '.', 'c', 'o', 'r', 'e', '.', 'B', 'i', 'n', 'd', 'C', 'o',
    'n', 'f', 'i', 'g', '\"', '\237', '\002', '\n', '\007', 'A', 'd', 'd',
    'r', 'e', 's', 's', '\022', 'L', '\n', '\016', 's', 'o', 'c', 'k',
    'e', 't', '_', 'a', 'd', 'd', 'r', 'e', 's', 's', '\030', '\001',
    ' ', '\001', '(', '\013', '2', '#', '.', 'e', 'n', 'v', 'o', 'y',
    '.', 'c', 'o', 'n', 'f', 'i', 'g', '.', 'c', 'o', 'r', 'e',
    '.', 'v', '3', '.', 'S', 'o', 'c', 'k', 'e', 't', 'A', 'd',
    'd', 'r', 'e', 's', 's', 'H', '\000', 'R', '\r', 's', 'o', 'c',
    'k', 'e', 't', 'A', 'd', 'd', 'r', 'e', 's', 's', '\022', '0',
    '\n', '\004', 'p', 'i', 'p', 'e', '\030', '\002', ' ', '\001', '(', '\013',
    '2', '\032', '.', 'e', 'n', 'v', 'o', 'y', '.', 'c', 'o', 'n',
    'f', 'i', 'g', '.', 'c', 'o', 'r', 'e', '.', 'v', '3', '.',
    'P', 'i', 'p', 'e', 'H', '\000', 'R', '\004', 'p', 'i', 'p', 'e',
    '\022', 'b', '\n', '\026', 'e', 'n', 'v', 'o', 'y', '_', 'i', 'n',
    't', 'e', 'r', 'n', 'a', 'l', '_', 'a', 'd', 'd', 'r', 'e',
    's', 's', '\030', '\003', ' ', '\001', '(', '\013', '2', '*', '.', 'e',
    'n', 'v', 'o', 'y', '.', 'c', 'o', 'n', 'f', 'i', 'g', '.',
    'c', 'o', 'r', 'e', '.', 'v', '3', '.', 'E', 'n', 'v', 'o',
    'y', 'I', 'n', 't', 'e', 'r', 'n', 'a', 'l', 'A', 'd', 'd',
    'r', 'e', 's', 's', 'H', '\000', 'R', '\024', 'e', 'n', 'v', 'o',
    'y', 'I', 'n', 't', 'e', 'r', 'n', 'a', 'l', 'A', 'd', 'd',
    'r', 'e', 's', 's', ':', ' ', '\232', '\305', '\210', '\036', '\033', '\n',
    '\031', 'e', 'n', 'v', 'o', 'y', '.', 'a', 'p', 'i', '.', 'v',
    '2', '.', 'c', 'o', 'r', 'e', '.', 'A', 'd', 'd', 'r', 'e',
    's', 's', 'B', '\016', '\n', '\007', 'a', 'd', 'd', 'r', 'e', 's',
    's', '\022', '\003', '\370', 'B', '\001', '\"', '\246', '\001', '\n', '\t', 'C',
    'i', 'd', 'r', 'R', 'a', 'n', 'g', 'e', '\022', '.', '\n', '\016',
    'a', 'd', 'd', 'r', 'e', 's', 's', '_', 'p', 'r', 'e', 'f',
    'i', 'x', '\030', '\001', ' ', '\001', '(', '\t', 'B', '\007', '\372', 'B',
    '\004', 'r', '\002', '\020', '\001', 'R', '\r', 'a', 'd', 'd', 'r', 'e',
    's', 's', 'P', 'r', 'e', 'f', 'i', 'x', '\022', 'E', '\n', '\n',
    'p', 'r', 'e', 'f', 'i', 'x', '_', 'l', 'e', 'n', '\030', '\002',
    ' ', '\001', '(', '\013', '2', '\034', '.', 'g', 'o', 'o', 'g', 'l',
    'e', '.', 'p', 'r', 'o', 't', 'o', 'b', 'u', 'f', '.', 'U',
    'I', 'n', 't', '3', '2', 'V', 'a', 'l', 'u', 'e', 'B', '\010',
    '\372', 'B', '\005', '*', '\003', '\030', '\200', '\001', 'R', '\t', 'p', 'r',
    'e', 'f', 'i', 'x', 'L', 'e', 'n', ':', '\"', '\232', '\305', '\210',
    '\036', '\035', '\n', '\033', 'e', 'n', 'v', 'o', 'y', '.', 'a', 'p',
    'i', '.', 'v', '2', '.', 'c', 'o', 'r', 'e', '.', 'C', 'i',
    'd', 'r', 'R', 'a', 'n', 'g', 'e', 'B', '\200', '\001', '\n', '\"',
    'i', 'o', '.', 'e', 'n', 'v', 'o', 'y', 'p', 'r', 'o', 'x',
    'y', '.', 'e', 'n', 'v', 'o', 'y', '.', 'c', 'o', 'n', 'f',
    'i', 'g', '.', 'c', 'o', 'r', 'e', '.', 'v', '3', 'B', '\014',
    'A', 'd', 'd', 'r', 'e', 's', 's', 'P', 'r', 'o', 't', 'o',
    'P', '\001', 'Z', 'B', 'g', 'i', 't', 'h', 'u', 'b', '.', 'c',
    'o', 'm', '/', 'e', 'n', 'v', 'o', 'y', 'p', 'r', 'o', 'x',
    'y', '/', 'g', 'o', '-', 'c', 'o', 'n', 't', 'r', 'o', 'l',
    '-', 'p', 'l', 'a', 'n', 'e', '/', 'e', 'n', 'v', 'o', 'y',
    '/', 'c', 'o', 'n', 'f', 'i', 'g', '/', 'c', 'o', 'r', 'e',
    '/', 'v', '3', ';', 'c', 'o', 'r', 'e', 'v', '3', '\272', '\200',
    '\310', '\321', '\006', '\002', '\020', '\002', 'b', '\006', 'p', 'r', 'o', 't',
    'o', '3',
};

static _upb_DefPool_Init *deps[8] = {
    &envoy_config_core_v3_extension_proto_upbdefinit,
    &envoy_config_core_v3_socket_option_proto_upbdefinit,
    &google_protobuf_wrappers_proto_upbdefinit,
    &envoy_annotations_deprecation_proto_upbdefinit,
    &udpa_annotations_status_proto_upbdefinit,
    &udpa_annotations_versioning_proto_upbdefinit,
    &validate_validate_proto_upbdefinit,
    NULL,
};

_upb_DefPool_Init envoy_config_core_v3_address_proto_upbdefinit = {
    deps,
    &envoy_config_core_v3_address_proto_upb_file_layout,
    "envoy/config/core/v3/address.proto",
    UPB_STRINGVIEW_INIT(descriptor, sizeof(descriptor)),
};
