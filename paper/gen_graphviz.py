#!/usr/bin/env python3

# (c) 2025 shdown
# This code is licensed under MIT license (see LICENSE.MIT for details)

import argparse
import re


class Node:
    def __init__(self):
        self.children = [None, None]
        self.on_cached_path = False
        self.on_insert_path = False
        self.on_custom_paths_mask = 0
        self.is_preleaf = False

    def set_on_cached_path_flag(self):
        self.on_cached_path = True

    def set_on_insert_path_flag(self):
        self.on_insert_path = True

    def set_on_custom_path(self, i):
        self.on_custom_paths_mask |= 1 << i

    def set_preleaf_flag(self):
        self.is_preleaf = True

    def insert(self, i):
        res = self.children[i]
        if res is None:
            res = Node()
            self.children[i] = res
        return res


class Tree:
    def __init__(self):
        self.root = Node()

    def insert(self, seq):
        node = self.root
        for c in seq:
            if c == '.':
                node = node.insert(0)
                node.set_preleaf_flag()
            else:
                node = node.insert(int(c))

    def mark(self, seq, mark_func):
        node = self.root

        should_mark = '/' not in seq

        if should_mark:
            mark_func(node)

        for c in seq:
            if c == '/':
                should_mark = True
                continue

            if c == '.':
                idx = 0
            else:
                idx = int(c)

            node = node.children[idx]
            assert node is not None
            if should_mark:
                mark_func(node)

    def _get_nodes_recursive(self, prefix, node, into_list):
        into_list.append((prefix, node))
        for i, child in enumerate(node.children):
            if child is not None:
                self._get_nodes_recursive(prefix + str(i), child, into_list)

    def get_nodes(self):
        res = []
        self._get_nodes_recursive('', self.root, res)
        return res

    def _get_edges_recursive(self, prefix, node, into_list):
        for i, child in enumerate(node.children):
            if child is not None:
                new_prefix = prefix + str(i)
                into_list.append((prefix, node, new_prefix, child))
                self._get_edges_recursive(new_prefix, child, into_list)

    def get_edges(self):
        res = []
        self._get_edges_recursive('', self.root, res)
        return res

    def _get_hacky_nodes_recursive(self, prefix, node, into_list):
        into_list.append((prefix, node))
        child_0, child_1 = node.children

        if child_0 is not None and child_0.on_cached_path:
            self._get_hacky_nodes_recursive(prefix + '0', child_0, into_list)
            return

        if child_1 is not None and child_1.on_cached_path:
            if child_0 is not None:
                self._get_nodes_recursive(prefix + '0', child_0, into_list)
            self._get_hacky_nodes_recursive(prefix + '1', child_1, into_list)
            return

    def get_hacky_nodes(self):
        res = []
        if self.root.on_cached_path:
            self._get_hacky_nodes_recursive('', self.root, res)
        return res

    def has_any_node(self, checker_func):
        for _, node in self.get_nodes():
            if checker_func(node):
                return True
        return False


class Params:
    def __init__(self, is_latex, latex_extra_options, graph_name, latex_caption):
        self.is_latex = is_latex
        self.latex_extra_options = latex_extra_options
        self.graph_name = graph_name
        self.latex_caption = latex_caption

    def print(self, s):
        if self.is_latex:
            s = re.sub(r'#([A-Fa-f0-9]{6})', r'\\MyColor{\1}', s)
        print(s)


class Color:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    @classmethod
    def from_hex(cls, s):
        assert len(s) == 7
        assert s[0] == '#'
        rr = s[1 : 3]
        gg = s[3 : 5]
        bb = s[5 : 7]
        return cls(
            r=int(rr, 16),
            g=int(gg, 16),
            b=int(bb, 16),
        )

    def as_graphviz_color(self):
        def int_to_hex(x):
            alphabet = '0123456789abcdef'
            return alphabet[x // 16] + alphabet[x % 16]
        return '#' + ''.join(int_to_hex(x) for x in [self.r, self.g, self.b])

    def adjust_brightness(self, e):
        def do_adjust_and_clamp(x):
            res = 255 * ((x / 255) ** e)
            return min(int(res), 255)

        return Color(
            r=do_adjust_and_clamp(self.r),
            g=do_adjust_and_clamp(self.g),
            b=do_adjust_and_clamp(self.b),
        )

    @classmethod
    def avg(cls, colors):
        n = len(colors)
        assert n

        def to_light(x):
            return (x / 255) ** 2

        def from_light(x):
            res = int((x ** 0.5) * 255)
            return min(res, 255)

        sigma_r_light = 0
        sigma_g_light = 0
        sigma_b_light = 0

        for color in colors:
            sigma_r_light += to_light(color.r)
            sigma_g_light += to_light(color.g)
            sigma_b_light += to_light(color.b)

        res_r = from_light(sigma_r_light / n)
        res_g = from_light(sigma_g_light / n)
        res_b = from_light(sigma_b_light / n)

        return cls(r=res_r, g=res_g, b=res_b)


class Style:
    def __init__(self, fg=None, bg=None, edge=None, attrs=None):
        self.purposes = {
            'fg': fg,
            'bg': bg,
            'edge': edge,
        }
        self.attrs = attrs

    @classmethod
    def from_hex(cls, fg=None, bg=None, edge=None, attrs=None):
        return cls(
            fg=Color.from_hex(fg) if fg is not None else None,
            bg=Color.from_hex(bg) if bg is not None else None,
            edge=Color.from_hex(edge) if edge is not None else None,
            attrs=attrs,
        )

    def for_purpose(self, purpose):
        return self.purposes[purpose]

    def as_graphviz(self, which_opts):
        chunks = []
        for opt, key in [('color', 'fg'), ('fillcolor', 'bg'), ('color', 'edge')]:
            value = self.purposes[key]
            if key in which_opts and value is not None:
                chunks.append(f'{opt} = "{value.as_graphviz_color()}";')

        if 'attrs' in which_opts and self.attrs is not None:
            for opt, value in self.attrs.items():
                if isinstance(value, str):
                    chunks.append(f'{opt} = "{value}";')
                else:
                    chunks.append(f'{opt} = {value};')

        return ' '.join(chunks)

    def clear_colors(self):
        self.purposes = {
            'fg': None,
            'bg': None,
            'edge': None,
        }

    def copy(self):
        return Style(
            fg=self.purposes['fg'],
            bg=self.purposes['bg'],
            edge=self.purposes['edge'],
            attrs=self.attrs,
        )

    def copy_attrs_from(self, other):
        self.attrs = other.attrs | self.attrs


CUSTOM_STYLES = [
    Style.from_hex(fg='#440000', bg='#ff7f7f', edge='#ff7f7f'),
    Style.from_hex(fg='#000044', bg='#7f7fff', edge='#7f7fff'),
]


NORMAL_NODE_STYLE = Style.from_hex(bg='#eef1aa', attrs=dict(style='filled'))


PRELEAF_NODE_STYLE = Style.from_hex(bg='#dddddd', attrs=dict(style='filled', shape='box'))


CACHED_PATH_STYLE = Style.from_hex(fg='#beff8e', attrs=dict(style='filled'))
CACHED_PATH_NODE_STYLE = Style.from_hex(bg='#9cd18d')


INSERT_PATH_NODE_STYLE = Style.from_hex(fg='#ff0000', bg='#ffb0b0', attrs=dict(style='dashed'))
INSERT_PATH_EDGE_STYLE = Style.from_hex(edge='#ff0000', attrs=dict(style='dashed'))


def choose_color_for_mask(purpose, mask, for_edge=False):
    colors = []
    for i, style in enumerate(CUSTOM_STYLES):
        if (mask >> i) & 1:
            colors.append(style.for_purpose(purpose))
    assert colors

    if for_edge:
        return Color.avg(colors).adjust_brightness(1.5)

    if len(colors) == 1:
        return colors[0]

    return Color.avg(colors)


def choose_attrs_for_mask(mask):
    if not (mask & (mask - 1)):
        return None
    return dict(penwidth=2)


def get_ident(prefix):
    if prefix:
        return 'n' + prefix
    else:
        return 'start'


def gen_header(tree, params):
    if params.is_latex:
        params.print(r'\begin{figure}[H]')
        if params.latex_caption:
            params.print(r'\caption{%s}' % params.latex_caption)
        params.print(r'\centering')

        if params.latex_extra_options:
            params.print(r'\digraph[%s]{%s}{' % (params.latex_extra_options, params.graph_name))
        else:
            params.print(r'\digraph{%s}{' % params.graph_name)
    else:
        params.print('digraph %s {' % params.graph_name)

    for what in ['graph', 'node', 'edge']:
        print(f'{what} [ fontname = "DejaVu Math TeX Gyre"; ]')

    params.print('layout = "dot";')
    params.print('node [')
    params.print(NORMAL_NODE_STYLE.as_graphviz(['fg', 'bg', 'attrs']))
    params.print(']')
    params.print('edge[weight=0]')


def gen_footer(tree, params):
    params.print('}')

    if params.is_latex:
        params.print(r'\end{figure}')


def gen_nodes(tree, params):
    for path, node in tree.get_nodes():
        ident = get_ident(path)

        if node.is_preleaf:
            label = '...'
        else:
            label = path or 'root'

        if node.on_cached_path:
            style = CACHED_PATH_NODE_STYLE

        elif node.on_insert_path and node.is_preleaf:
            style = INSERT_PATH_NODE_STYLE.copy()
            style.copy_attrs_from(PRELEAF_NODE_STYLE)

        elif node.on_insert_path:
            style = INSERT_PATH_NODE_STYLE

        elif node.is_preleaf:
            style = PRELEAF_NODE_STYLE

        elif node.on_custom_paths_mask:
            mask = node.on_custom_paths_mask
            color_fg = choose_color_for_mask('fg', mask)
            color_bg = choose_color_for_mask('bg', mask)
            attrs = choose_attrs_for_mask(mask)
            style = Style(fg=color_fg, bg=color_bg, attrs=attrs)
        else:
            style = Style()

        style_str = style.as_graphviz(['fg', 'bg', 'attrs'])
        params.print(f'"{ident}" [ label = "{label}"; {style_str} ]')


def gen_edges(tree, params):
    edges = tree.get_edges()

    def print_edges(cached_path_criterion, style_func):
        for prefix_from, node_from, prefix_to, node_to in edges:

            edge_is_on_cached_path = node_from.on_cached_path and node_to.on_cached_path
            if edge_is_on_cached_path != cached_path_criterion:
                continue

            src_ident = get_ident(prefix_from)
            dst_ident = get_ident(prefix_to)

            style = style_func(node_from, node_to)
            if style is not None:
                attrs_str = style.as_graphviz(['edge', 'attrs'])
                params.print(f'{src_ident} -> {dst_ident} [ {attrs_str} ];')
            else:
                params.print(f'{src_ident} -> {dst_ident};')

    def normal_edge_style_func(node_from, node_to):
        if node_to.on_insert_path:
            return INSERT_PATH_EDGE_STYLE

        maskF = node_from.on_custom_paths_mask
        maskT = node_to.on_custom_paths_mask
        for mask in [maskF & maskT, maskT]:
            if mask:
                color = choose_color_for_mask('edge', mask, for_edge=True)
                return Style(edge=color)

        return None

    print_edges(
        cached_path_criterion=False,
        style_func=normal_edge_style_func)

    params.print('subgraph cluster_cached_path {')
    params.print('label = "Cached path";')
    params.print(CACHED_PATH_STYLE.as_graphviz(['fg', 'bg', 'attrs']))

    print_edges(
        cached_path_criterion=True,
        style_func=lambda node_from, node_to: None)

    params.print('}')


def gen_dirty_hack(tree, params):
    hacky_nodes = tree.get_hacky_nodes()
    buckets = {}
    for prefix, node in hacky_nodes:
        buckets.setdefault(len(prefix), []).append(prefix)
    sorted_buckets = sorted(buckets.items())

    if tree.has_any_node(lambda node: node.is_preleaf):
        if sorted_buckets:
            sorted_buckets.pop()

    chunks = []
    for depth, prefixes in sorted_buckets:
        inner = ', '.join(get_ident(prefix) for prefix in prefixes)
        if len(prefixes) == 1:
            chunks.append(inner)
        else:
            chunks.append('{' + inner + '}')

    params.print('edge[style=invis,weight=1]')
    params.print(' -> '.join(chunks) + ';')


def generate(tree, params):
    gen_header(tree, params)

    gen_nodes(tree, params)

    gen_edges(tree, params)

    gen_dirty_hack(tree, params)

    gen_footer(tree, params)


def main():
    def parse_custom_path(s):
        idx, path = s.split(':')
        return int(idx), path

    ap = argparse.ArgumentParser()
    ap.add_argument('nodes')
    ap.add_argument('--cached-path', default='')
    ap.add_argument('--insert-path', default='')
    ap.add_argument('--graph-name', default='G')
    ap.add_argument('--custom-path', type=parse_custom_path, action='append')
    ap.add_argument('--latex', action='store_true')
    ap.add_argument('--latex-extra-opts', default='')
    ap.add_argument('--latex-caption', default='')
    args = ap.parse_args()

    tree = Tree()

    for seq in args.nodes.split(','):
        tree.insert(seq)

    if args.cached_path:
        tree.mark(args.cached_path, lambda node: node.set_on_cached_path_flag())

    if args.insert_path:
        tree.mark(args.insert_path, lambda node: node.set_on_insert_path_flag())

    if args.custom_path is not None:
        NORMAL_NODE_STYLE.clear_colors()

        for i, path in args.custom_path:
            tree.mark(path, lambda node: node.set_on_custom_path(i))

    params = Params(
        is_latex=args.latex,
        latex_extra_options=args.latex_extra_opts,
        graph_name=args.graph_name,
        latex_caption=args.latex_caption)

    generate(tree, params)


if __name__ == '__main__':
    main()
