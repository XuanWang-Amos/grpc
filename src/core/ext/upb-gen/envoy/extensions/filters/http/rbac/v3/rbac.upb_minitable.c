/* This file was generated by upb_generator from the input file:
 *
 *     envoy/extensions/filters/http/rbac/v3/rbac.proto
 *
 * Do not edit -- your changes will be discarded when the file is
 * regenerated. */

#include <stddef.h>
#include "upb/generated_code_support.h"
#include "envoy/extensions/filters/http/rbac/v3/rbac.upb_minitable.h"
#include "envoy/config/rbac/v3/rbac.upb_minitable.h"
#include "xds/annotations/v3/status.upb_minitable.h"
#include "xds/type/matcher/v3/matcher.upb_minitable.h"
#include "udpa/annotations/migrate.upb_minitable.h"
#include "udpa/annotations/status.upb_minitable.h"
#include "udpa/annotations/versioning.upb_minitable.h"

// Must be last.
#include "upb/port/def.inc"

static const upb_MiniTableSub envoy_extensions_filters_http_rbac_v3_RBAC_submsgs[4] = {
  {.UPB_PRIVATE(submsg) = &envoy__config__rbac__v3__RBAC_msg_init},
  {.UPB_PRIVATE(submsg) = &envoy__config__rbac__v3__RBAC_msg_init},
  {.UPB_PRIVATE(submsg) = &xds__type__matcher__v3__Matcher_msg_init},
  {.UPB_PRIVATE(submsg) = &xds__type__matcher__v3__Matcher_msg_init},
};

static const upb_MiniTableField envoy_extensions_filters_http_rbac_v3_RBAC__fields[5] = {
  {1, UPB_SIZE(12, 16), 64, 0, 11, (int)kUpb_FieldMode_Scalar | ((int)UPB_SIZE(kUpb_FieldRep_4Byte, kUpb_FieldRep_8Byte) << kUpb_FieldRep_Shift)},
  {2, UPB_SIZE(16, 24), 65, 1, 11, (int)kUpb_FieldMode_Scalar | ((int)UPB_SIZE(kUpb_FieldRep_4Byte, kUpb_FieldRep_8Byte) << kUpb_FieldRep_Shift)},
  {3, UPB_SIZE(28, 32), 0, kUpb_NoSub, 9, (int)kUpb_FieldMode_Scalar | ((int)kUpb_FieldRep_StringView << kUpb_FieldRep_Shift)},
  {4, UPB_SIZE(20, 48), 66, 2, 11, (int)kUpb_FieldMode_Scalar | ((int)UPB_SIZE(kUpb_FieldRep_4Byte, kUpb_FieldRep_8Byte) << kUpb_FieldRep_Shift)},
  {5, UPB_SIZE(24, 56), 67, 3, 11, (int)kUpb_FieldMode_Scalar | ((int)UPB_SIZE(kUpb_FieldRep_4Byte, kUpb_FieldRep_8Byte) << kUpb_FieldRep_Shift)},
};

const upb_MiniTable envoy__extensions__filters__http__rbac__v3__RBAC_msg_init = {
  &envoy_extensions_filters_http_rbac_v3_RBAC_submsgs[0],
  &envoy_extensions_filters_http_rbac_v3_RBAC__fields[0],
  UPB_SIZE(40, 64), 5, kUpb_ExtMode_NonExtendable, 5, UPB_FASTTABLE_MASK(24), 0,
#ifdef UPB_TRACING_ENABLED
  "envoy.extensions.filters.http.rbac.v3.RBAC",
#endif
  UPB_FASTTABLE_INIT({
    {0x0000000000000000, &_upb_FastDecoder_DecodeGeneric},
    {0x0000000000000000, &_upb_FastDecoder_DecodeGeneric},
    {0x0000000000000000, &_upb_FastDecoder_DecodeGeneric},
    {0x002000003f00001a, &upb_pss_1bt},
  })
};

static const upb_MiniTableSub envoy_extensions_filters_http_rbac_v3_RBACPerRoute_submsgs[1] = {
  {.UPB_PRIVATE(submsg) = &envoy__extensions__filters__http__rbac__v3__RBAC_msg_init},
};

static const upb_MiniTableField envoy_extensions_filters_http_rbac_v3_RBACPerRoute__fields[1] = {
  {2, UPB_SIZE(12, 16), 64, 0, 11, (int)kUpb_FieldMode_Scalar | ((int)UPB_SIZE(kUpb_FieldRep_4Byte, kUpb_FieldRep_8Byte) << kUpb_FieldRep_Shift)},
};

const upb_MiniTable envoy__extensions__filters__http__rbac__v3__RBACPerRoute_msg_init = {
  &envoy_extensions_filters_http_rbac_v3_RBACPerRoute_submsgs[0],
  &envoy_extensions_filters_http_rbac_v3_RBACPerRoute__fields[0],
  UPB_SIZE(16, 24), 1, kUpb_ExtMode_NonExtendable, 0, UPB_FASTTABLE_MASK(255), 0,
#ifdef UPB_TRACING_ENABLED
  "envoy.extensions.filters.http.rbac.v3.RBACPerRoute",
#endif
};

static const upb_MiniTable *messages_layout[2] = {
  &envoy__extensions__filters__http__rbac__v3__RBAC_msg_init,
  &envoy__extensions__filters__http__rbac__v3__RBACPerRoute_msg_init,
};

const upb_MiniTableFile envoy_extensions_filters_http_rbac_v3_rbac_proto_upb_file_layout = {
  messages_layout,
  NULL,
  NULL,
  2,
  0,
  0,
};

#include "upb/port/undef.inc"

