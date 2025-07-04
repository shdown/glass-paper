Paper: https://arxiv.org/abs/2506.13991

Mirror on GitHub Pages: https://shdown.github.io/stuff/glass-paper.pdf

This repository contains:
 * source code for *glass*;
 * minimal example and build script;
 * documentation of the build process and code organization;
 * documentation of the configuration macros.
 * LaTeX sources of the paper.

Will possibly be added in the future:
 * benchmarking code and data.

# Build process

## The external preprocessor: `ato`

*Glass* uses an external pre-processor that helps in writing “X macro”-styled generic code,
and also managing macros (undefining them in the end), including settings that are passed as preprocessor defines.

The code including the glass source must define `GLASS_PREFIX`; all functions will be prefixed with it.
For example, if `GLASS_PREFIX` is `my_glass`, the creation function will be called `my_glass_create`.
In order to do this, we define `GLASS_NAME(SUFFIX)` macro that concatenates
together (with `##`) `GLASS_PREFIX`, literal “`_`” and `SUFFIX`.
The name of the function then can be written as `GLASS_NAME(create)`.

The pre-processor allows us to write `@create` instead of `GLASS_NAME(create)`.

It also serves to reduce error-prone boilerplate related to keeping track of macros that should be
undefined in the end, including the settings definitions.

The preprocessor is called “ato”, because that’s the name of the “@” character in Japanese.

## Code organization

There are two separate `ato` projects in the tree: `glass.ato` and `glass_prevnext.ato`.
All other `.ato` files are supposed to be included from `glass.ato`, rather than be operated upon by `ato.py` directly.

So two first build steps are:

```
./ato.py glass_prevnext.ato > glass_prevnext.h
./ato.py glass.ato > glass.h
```

Then you can include `glass.h` in your code after defining some configuration macros (see below).
See the minimal example in the `example/` directory.

### Other auto-generated files

There are two other source files that has been auto-generated:
 * `glass_c.inc` is generated by `gen_glass_c.py`;
 * `glass_invmod.inc` is generated by `gen_invmod.py`.

Both `.inc` and `.py` files mentioned above are provided in the repo.

# Configuration macros

Required:
 * `GLASS_PREFIX`: the prefix for all glass structures and functions;
 * `GLASS_N`: max number of children of a single node (must be a power of two);
 * `GLASS_SIZE`: unsigned integer type to use for index-pointers (analogous to `size_t`, but can be a smaller type in order to save memory and improve cache utilization);
 * `GLASS_KEY`: unsigned integer type to use for a key;
 * `GLASS_K`: maximum number of bits in a key (bits above `[0; GLASS_K)` must always be zero in a key).

Optional:
 * `GLASS_WITH_SSIZE` (0 or 1): whether or not `GLASS_SIZE` values can be used as signed values (effectively halving the number of indices that can be represented), which probably can give some small speed-up. If enabled, `GLASS_SSIZE` must also be defined.
 * `GLASS_SSIZE`: if `GLASS_WITH_SSIZE` is enabled, must be defined to the signed counterpart for the `GLASS_SIZE` type.
 * `GLASS_WITH_TRASH_ENCODING` (0 or 1): whether or not to use *trash encoding* (see section 5.5 of the paper for details).
 * `GLASS_WITH_ADD_NODE_MULTIPLE` (0 or 1): whether or not to use multiple-node allocation.
 * `GLASS_WITH_CACHE` (0 or 1): whether or not to use *cached path* (see section 5.1 of the paper for details).
 * `GLASS_STATS_CALLBACK`: (**Never use in production — will cause great slowdown!**) If defined, the callback specified by this macro will be called on certain events (for profiling). See the “Stats callback” section for details. If defined, must be either a function macro or a name of a function.
 * `GLASS_WITH_FIRST_LAST_PTRS` (0 or 1): whether or not to cache iterators to the first and last elements (see section 5.4 of the paper for details).
 * `GLASS_WITH_FIRST_LAST_PTRS_LAZY` (0 or 1): if `GLASS_WITH_FIRST_LAST_PTRS` is enabled, whether or not the first/last iterators cache should be lazy (see section 5.4 of the paper for details).
 * `GLASS_WITH_HT` (0 or 1): whether or not to use *hash table* (or, rather, a *cache table*) (see section 5.2 of the paper for details).
 * `GLASS_WITH_HT_PREV_PTR` (0 or 1): whether or not the hash table chains should be doubly-linked (as opposed to singly-linked). Although disabling this saves some memory, in such a case a deletion from the hash table is no longer guaranteed to be hard O(1).
 * `GLASS_HT_MAX_LOOKUP_LEN`: how many first elements of the chain are to be examined during the hash table lookup before giving up and returning “don’t know” answer. Defaults to 5.
 * `GLASS_WITH_HT_HEALTH_CHECKS` (0 or 1): (**Never enable in production — will cause insane slowdown!**) whether or not to perform very costly, O(n) health-checks each time a hash table is accessed.
 * `GLASS_WITH_ASM` (0 or 1): whether or not to use intrinsics specific to x86-64 architecture and BMI2 instruction set. Note that this restricts `GLASS_N` to be <= 8.
 * `GLASS_WITH_ASSERTS` (0 or 1): whether or not to use run-time asserts (with `assert` from `<assert.h>`). If enabled, expect some slowdown.
 * `GLASS_WITH_COMPAT_SHIM` (0 or 1): (**Only enable if compiling with old version of gcc/clang — otherwise there will be unnecessary slowdown!**) whether or not to roll our own implementations for `__builtin_popcountg`, `__builtin_ctzg` and `__builtin_clzg` (our versions are slower for two-argument versions of ctz/clz). Note that this restricts `GLASS_N` to be <= 8.
 * `GLASS_ALLOCATOR`: the custom allocator function to use. Must have the following signature: `void *allocator(int op, void *p, size_t old_n, size_t new_n, size_t elem_sz)`; op=0 means reallocate, op=1 means free.

# Stats callback

Again, **never define `GLASS_STATS_CALLBACK` in production — it will cause great slowdown!**

If `GLASS_STATS_CALLBACK` is defined, it is expected to take two arguments: `(int channel, int value)`.
Below, `@x` means `${GLASS_PREFIX}_${x}`; e.g. if `GLASS_PREFIX` is `my_glass`, `@_CHANNEL_CACHE` means `my_glass__CHANNEL_CACHE`.

`channel` is either of `@_CHANNEL_*` enum constants.
The meaning of `value` depends on the value of `channel`:
 * `@_CHANNEL_CACHE`: a cache lookup has just resulted in depth of `value`;
 * `@_CHANNEL_GROW_VEC`: the nodes vector has just been doubled in capacity; `value` is always zero;
 * `@_CHANNEL_HINT_CLIMB_UP`: in order to locate an element by a hint, we have just climbed `value` levels up;
 * `@_CHANNEL_TDFIND_NEXTPREV`: “`TDfind_nextprev_or_eq`” operation has just finished in `value` steps (this count doesn’t include the number of steps of “`TDfind_first_or_last`”, which possibly executes in the end of this operation);
 * `@_CHANNEL_TDFIND_FIRSTLAST`: “`TDfind_first_or_last`” operation has just finished in `value` steps;
 * `@_CHANNEL_QFIND_UP`: the “go up” phase of “`Qfind`” operation has just finished in `value` steps;
 * `@_CHANNEL_QFIND_DOWN`: the “go down” phase of “`Qfind`” operation has just finished in `value` steps;
 * `@_CHANNEL_ERASE`: the “erase” operation has just finished in `value` steps;
 * `@_CHANNEL_CLIMB_DOWN`: the “climb down” operation has just finished in `value` steps;
 * `@_CHANNEL_SAMSARA`: the “samsara” thing (creation of new nodes in order to insert a new element) has just finished, ending up creating `value` new nodes;
 * `@_CHANNEL_HT_LOOKUP`: a hash-table lookup has just produced the result of…
    - `value = 2`: “the key is present”;
    - `value = 1`: “the key is **not** present”;
    - `value = 0`: “don’t know”.

Run `grep '@_CHANNEL_.*,$' glass.ato` for a list that is guaranteed to be up-to-date.

# The paper

The LaTeX code of the paper (as well as all the other stuff needed to compile it) is located in the `paper/` directory.

In order to compile it, change current directory to `paper/` and run `./compile.sh`.

`compile.sh` doesn’t run `gen_pdunno.sh` script because this takes a lot of time (on my machine, 132 seconds with PyPy, 273 seconds with CPython).
Instead, pre-generated `pdunnoRAW.txt`, `pdunnoMINUS.txt` and `pdunnoPLUS.txt` are provided in the repo.
