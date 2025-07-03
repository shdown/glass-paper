// (c) 2025 shdown
// This code is licensed under MIT license (see LICENSE.MIT for details)

#ifdef __cplusplus
extern "C" {
#endif

#include "common.h"

void *realloc_or_die(void *p, size_t n, size_t m)
{
    void *q;
    size_t sz;
    if (unlikely(__builtin_mul_overflow(n, m, &sz))) {
        goto oom;
    }

    q = realloc(p, sz);
    if (unlikely(!q && sz)) {
        goto oom;
    }

    return q;

oom:
    die_out_of_memory();
}

void *calloc_or_die(size_t n, size_t m)
{
    void *r = calloc(n, m);
    if (unlikely(!r && n && m)) {
        die_out_of_memory();
    }
    return r;
}

void *malloc_or_die(size_t n, size_t m)
{
    return realloc_or_die(NULL, n, m);
}

void *x2realloc_or_die(void *p, size_t *n, size_t m)
{
    if (*n == 0) {
        *n = 1;
    } else {
        if (unlikely(__builtin_mul_overflow(*n, 2u, n))) {
            die_out_of_memory();
        }
    }
    return realloc_or_die(p, *n, m);
}

void *memdup_or_die(const void *p, size_t n)
{
    if (!n)
        return NULL;

    void *q = malloc(n);
    if (unlikely(!q))
        die_out_of_memory();

    memcpy(q, p, n);
    return q;
}

char *strdup_or_die(const char *s)
{
    return (char *) memdup_or_die(s, strlen(s) + 1);
}

char *allocvf_or_die(const char *fmt, va_list vl)
{
    int n;
    size_t nr;
    char *r;
    va_list vl2;
    va_copy(vl2, vl);

    n = vsnprintf(NULL, 0, fmt, vl);
    if (unlikely(n < 0))
        goto fail;

    nr = ((size_t) n) + 1;
    r = (char *) malloc_or_die(nr, sizeof(char));
    if (unlikely(vsnprintf(r, nr, fmt, vl2) < 0))
        goto fail;

    va_end(vl2);
    return r;

fail:
    fputs("FATAL: allocvf_or_die: vsnprintf() failed.\n", stderr);
    abort();
}

char *allocf_or_die(const char *fmt, ...)
{
    va_list vl;
    va_start(vl, fmt);
    char *r = allocvf_or_die(fmt, vl);
    va_end(vl);
    return r;
}

#ifdef __cplusplus
} // extern "C"
#endif
