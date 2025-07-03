// (c) 2025 shdown
// This code is licensed under MIT license (see LICENSE.MIT for details)

#pragma once

#if __cplusplus
extern "C" {
#endif

#include "../common.h"

#if __cplusplus
}
#endif

#define GLASS_N 32
#define GLASS_WITH_ASM 1
#define GLASS_PREFIX glass
#define GLASS_SIZE uint16_t
#define GLASS_KEY uint64_t
#define GLASS_K 50

#include "../glass.h"
