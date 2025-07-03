// (c) 2025 shdown
// This code is licensed under MIT license (see LICENSE.MIT for details)


#pragma once

#include <stdlib.h>
#include <stddef.h>
#include <stdint.h>
#include <limits.h>
#include <inttypes.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include <stdarg.h>
#include <assert.h>
#include <time.h>
#include <signal.h>
#include <pthread.h>
#include <errno.h>
#include <unistd.h>

#define in_header       static inline __attribute__((unused))
#define likely(E)       __builtin_expect((E), 1)
#define unlikely(E)     __builtin_expect((E), 0)
#define array_size(A)   (sizeof(A) / sizeof((A)[0]))

in_header __attribute__((noreturn))
void die_out_of_memory(void)
{
    fputs("Out of memory.\n", stderr);
    abort();
}

void *realloc_or_die(void *p, size_t n, size_t m);

void *calloc_or_die(size_t n, size_t m);

void *malloc_or_die(size_t n, size_t m);

void *x2realloc_or_die(void *p, size_t *n, size_t m);

void *memdup_or_die(const void *p, size_t n);

char *strdup_or_die(const char *s);

__attribute__((format(printf, 1, 0)))
char *allocvf_or_die(const char *fmt, va_list vl);

__attribute__((format(printf, 1, 2)))
char *allocf_or_die(const char *fmt, ...);
