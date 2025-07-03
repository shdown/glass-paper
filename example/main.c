// (c) 2025 shdown
// This code is licensed under MIT license (see LICENSE.MIT for details)

#if __cplusplus
extern "C" {
#endif

#include "../common.h"

#if __cplusplus
}
#endif

#include "glass_def.h"

int main()
{
    glass_Glass g;

    glass_create(&g, 0);

    glass_destroy(&g);
}
