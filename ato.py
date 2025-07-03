#!/usr/bin/env python3

# (c) 2025 shdown
# This code is licensed under MIT license (see LICENSE.MIT for details)

import re
import os
import sys
import argparse


C_TOKEN_RE_STR = r'[A-Za-z_][A-Za-z_0-9]*'


MACRO_RE = re.compile(r'^#\s*define\s*(@?' + C_TOKEN_RE_STR + r')')


ATO_RE = re.compile(r'@([~#]?)(' + C_TOKEN_RE_STR + r')')


class Macro:
    def __init__(self, name, body):
        self.name = name
        self.body = body


class Project:
    def __init__(self, name=None, include_root='.'):
        self.name = name
        self.namespace = None
        self.include_root = include_root
        self._include_once_set = set()
        self._undef_macros = {}

    def require_name(self):
        if self.name is None:
            raise ValueError('project name was not set ("@@project" directive)')
        return self.name

    def require_namespace(self):
        if self.namespace is None:
            raise ValueError('namespace was not set ("@@namespace" directive)')
        return self.namespace

    def should_include_once(self, path):
        if path in self._include_once_set:
            return False
        self._include_once_set.add(path)
        return True

    def add_to_undef_macros(self, macro_name, must_be_defined=True):
        self._undef_macros[macro_name] = must_be_defined or self._undef_macros.get(macro_name, True)

    def keep_macro_defined(self, macro_name):
        try:
            del self._undef_macros[macro_name]
        except KeyError:
            pass

    def get_undef_macros(self):
        return self._undef_macros.items()


class Preprocessor:
    EXPANSIONS = {
        'force_inline':    'static inline __attribute__((unused, always_inline))',
        'inline':          'static inline __attribute__((unused))',
        'no_inline':       'static __attribute__((unused))',
        'force_no_inline': 'static __attribute__((unused, noinline))',
    }

    def __init__(self, mode, reader, emitter, project):
        self._mode = mode
        self._reader = reader
        self._emitter = emitter
        self._project = project
        self._atoato_directives = {
            '@@project':         (self._set_project_name, 'p'),
            '@@namespace':       (self._set_namespace, 'n'),

            '@@boilerplate':     (self._handle_boilerplate, 'p'),

            '@@include':         (self._handle_include, '*'),
            '@@include_once':    (self._handle_include_once, '*'),

            '@@permanent':       (self._handle_permanent, 'p'),
            '@@require':         (self._handle_require, 'p'),
            '@@config':          (self._handle_config, 'p'),
            '@@config_save':     (self._handle_config_save, 'p'),
            '@@temp':            (self._handle_temp, 'p'),

            '@@ntemp':           (self._handle_ntemp, 'n'),

            '@@keep':            (self._handle_keep, 'p'),
            '@@undef':           (self._handle_undef, 'p'),
        }

    def _add_to_undef(self, macro_name, must_be_defined):
        self._project.add_to_undef_macros(macro_name, must_be_defined=must_be_defined)

    def _perform_at_subst(self, line):
        def substitute(m):
            sigil, token = m.group(1), m.group(2)
            if sigil == '~':
                result = Preprocessor.EXPANSIONS.get(token)
                if result is None:
                    raise ValueError(f'unknown expansion "@~{token}"')
                return result
            else:
                if self._mode == 'p':
                    pn = self._project.require_name()
                    if sigil == '#':
                        return f'{pn}_{token}'
                    else:
                        return f'{pn}_NAME({token})'
                else:
                    if sigil:
                        raise ValueError(f'expansion "@{sigil}" is not supported in mode "n"')
                    namespace = self._project.require_namespace()
                    return f'{pn}_{token}'
        return ATO_RE.sub(substitute, line)

    def _process_line(self, line):
        if line.startswith('@@'):
            words = line.split()
            directive = words[0]
            handler, mode = self._atoato_directives.get(directive)
            if handler is None:
                raise ValueError(f'unknown directive "{directive}"')
            if mode != '*' and mode != self._mode:
                raise ValueError(f'directive "{directive}" is not supported in mode "{self._mode}"')
            handler(words[1:])
        elif line.startswith('@='):
            self._emitter.emit(line[2:])
        else:
            self._emitter.emit(self._perform_at_subst(line))

    def _read_macro(self, require_and_accept_leading_at=False):
        line = self._reader.read_line(raise_on_eof=True)
        m = MACRO_RE.match(line)
        if not m:
            raise ValueError('unexpected macro format')
        name = m.group(1)

        if require_and_accept_leading_at:
            if not name.startswith('@'):
                raise ValueError('unexpected macro name (does not start with "@")')
        else:
            if name.startswith('@'):
                raise ValueError('unexpected macro name (starts with "@")')

        lines = [line]
        while line.endswith('\\'):
            line = self._reader.read_line(raise_on_eof=True)
            lines.append(line)

        body = '\n'.join(self._perform_at_subst(line) for line in lines)
        return Macro(name=name, body=body)

    def _handle_boilerplate(self, args):
        if args:
            raise ValueError('@@boilerplate must take no arguments')

        pn = self._project.require_name()

        self._emitter.emit(f'#ifndef {pn}_PREFIX')
        self._emitter.emit(f'#error "You must define {pn}_PREFIX."')
        self._emitter.emit(f'#endif')

        self._emitter.emit(f'#define {pn}_CAT1(X_, Y_) X_ ## _ ## Y_')
        self._emitter.emit(f'#define {pn}_CAT(X_, Y_) {pn}_CAT1(X_, Y_)')
        self._emitter.emit(f'#define {pn}_NAME(Suffix_) {pn}_CAT({pn}_PREFIX, Suffix_)')

        self._emitter.emit(f'#define {pn}_STRINGIFY1(X_) #X_')
        self._emitter.emit(f'#define {pn}_STRINGIFY(X_) {pn}_STRINGIFY1(X_)')

        for suffix in 'PREFIX CAT1 CAT NAME STRINGIFY1 STRINGIFY'.split():
            self._add_to_undef(f'{pn}_{suffix}', must_be_defined=True)

    def _set_project_name(self, args):
        if len(args) != 1:
            raise ValueError('@@project must take 1 argument')
        self._project.name = args[0]

    def _set_namespace(self, args):
        if len(args) != 1:
            raise ValueError('@@namespace must take 1 argument')
        self._project.namespace = args[0]

    def _handle_permanent(self, args):
        if args:
            raise ValueError('@@permanent must take no arguments')

        macro = self._read_macro()

        self._emitter.emit(f'#ifdef {macro.name}')
        self._emitter.emit(f'#undef {macro.name}')
        self._emitter.emit(f'#endif')

        self._emitter.emit(macro.body)

    def _handle_require(self, args):
        if len(args) != 1:
            raise ValueError('@@require must take 1 argument')

        param = args[0]

        self._emitter.emit(f'#ifndef {param}')
        self._emitter.emit(f'#error "You must define {param}."')
        self._emitter.emit(f'#endif')

        self._add_to_undef(param, must_be_defined=False)

    def _handle_config(self, args):
        if args:
            raise ValueError('@@config must take no arguments')

        macro = self._read_macro()

        self._emitter.emit(f'#ifndef {macro.name}')
        self._emitter.emit(macro.body)
        self._emitter.emit(f'#endif')

        self._add_to_undef(macro.name, must_be_defined=False)

    def _handle_config_save(self, args):
        if len(args) != 1:
            raise ValueError('@@config_save must take 1 argument')

        save_into_ppvar = args[0]

        macro = self._read_macro()

        if macro.name == save_into_ppvar:
            raise ValueError('trying to save #ifdef of macro into itself')

        self._emitter.emit(f'#ifdef {macro.name}')
        self._emitter.emit(f'#define {save_into_ppvar} 1')
        self._emitter.emit(f'#else')
        self._emitter.emit(f'#define {save_into_ppvar} 0')
        self._emitter.emit(macro.body)
        self._emitter.emit(f'#endif')

        self._add_to_undef(macro.name, must_be_defined=False)
        self._add_to_undef(save_into_ppvar, must_be_defined=False)

    def _handle_temp(self, args):
        if args:
            raise ValueError('@@temp must take no arguments')

        macro = self._read_macro()
        self._emitter.emit(macro.body)

        self._add_to_undef(macro.name, must_be_defined=False)

    def _handle_ntemp(self, args):
        if args:
            raise ValueError('@@ntemp must take no arguments')

        macro = self._read_macro(require_and_accept_leading_at=True)

        namespace = self._project.require_namespace()
        actual_macro_name = namespace + macro.name[1:]

        self._emitter.emit(macro.body)

        self._add_to_undef(actual_macro_name, must_be_defined=False)

    def _handle_keep(self, args):
        if not args:
            raise ValueError('@@keep must take at least one argument')
        for arg in args:
            self._project.keep_macro_defined(arg)

    def _handle_undef(self, args):
        if not args:
            raise ValueError('@@undef must take at least one argument')
        for arg in args:
            self._add_to_undef(arg, must_be_defined=False)

    def _handle_include_internal(self, path, once):
        if once:
            if not self._project.should_include_once(path):
                return

        path = os.path.join(self._project.include_root, path)

        with open(path, 'r') as f:
            new_reader = FileReader(f)
            pp = Preprocessor(
                mode=self._mode,
                reader=new_reader,
                emitter=self._emitter,
                project=self._project)
            pp.preprocess(finalize=False)

    def _handle_include(self, args):
        if len(args) != 1:
            raise ValueError('@@include must take exactly one argument')
        self._handle_include_internal(args[0], once=False)

    def _handle_include_once(self, args):
        if len(args) != 1:
            raise ValueError('@@include_once must take exactly one argument')
        self._handle_include_internal(args[0], once=True)

    def finalize(self):
        for macro_name, must_be_defined in self._project.get_undef_macros():
            if must_be_defined:
                self._emitter.emit(f'#undef {macro_name}')
            else:
                self._emitter.emit(f'#ifdef {macro_name}')
                self._emitter.emit(f'#undef {macro_name}')
                self._emitter.emit(f'#endif')

    def preprocess(self, finalize=True):
        while True:
            line = self._reader.read_line()
            if line is None:
                break
            self._process_line(line)
        if finalize:
            self.finalize()


class FileEmitter:
    def __init__(self, f):
        self._f = f

    def emit(self, line):
        print(line, file=self._f)


class FileReader:
    def __init__(self, f):
        self._f = f

    def read_line(self, raise_on_eof=False):
        line = self._f.readline()
        if line:
            return line.rstrip('\n')
        if raise_on_eof:
            raise EOFError()
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('input_file', type=lambda path: open(path, 'r'), default=sys.stdin, nargs='?')
    ap.add_argument('output_file', type=lambda path: open(path, 'w'), default=sys.stdout, nargs='?')
    ap.add_argument('--namespace-mode', action='store_true')
    ap.add_argument('--project-name', default=None)
    ap.add_argument('--include-root', default='.')
    ap.add_argument('--no-finalize', action='store_true')

    args = ap.parse_args()

    if args.namespace_mode and args.project_name is not None:
        raise ValueError('Option "--namespace-mode" is incompatible with "--project-name"')

    reader = FileReader(args.input_file)
    emitter = FileEmitter(args.output_file)
    pp = Preprocessor(
        mode='n' if args.namespace_mode else 'p',
        reader=reader,
        emitter=emitter,
        project=Project(
            name=args.project_name,
            include_root=args.include_root,
        ),
    )
    pp.preprocess(finalize=not args.no_finalize)


if __name__ == '__main__':
    main()
