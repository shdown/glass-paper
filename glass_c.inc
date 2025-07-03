#if GLASS_N == 2
#define GLASS__C 1
#elif GLASS_N == 4
#define GLASS__C 2
#elif GLASS_N == 8
#define GLASS__C 3
#elif GLASS_N == 16
#define GLASS__C 4
#elif GLASS_N == 32
#define GLASS__C 5
#elif GLASS_N == 64
#define GLASS__C 6
#elif GLASS_N == 128
#define GLASS__C 7
#elif GLASS_N == 256
#define GLASS__C 8
#elif GLASS_N == 512
#define GLASS__C 9
#elif GLASS_N == 1024
#define GLASS__C 10
#elif GLASS_N == 2048
#define GLASS__C 11
#elif GLASS_N == 4096
#define GLASS__C 12
#elif GLASS_N == 8192
#define GLASS__C 13
#elif GLASS_N == 16384
#define GLASS__C 14
#elif GLASS_N == 32768
#define GLASS__C 15
#elif GLASS_N == 65536
#define GLASS__C 16
#elif GLASS_N == 131072
#define GLASS__C 17
#elif GLASS_N == 262144
#define GLASS__C 18
#elif GLASS_N == 524288
#define GLASS__C 19
#elif GLASS_N == 1048576
#define GLASS__C 20
#else
#error "GLASS_N is too big, not a power of two, or otherwise defined to something wrong."
#endif
@@undef GLASS__C
