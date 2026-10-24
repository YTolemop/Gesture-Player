"""Choose an installed CJK font for Tk and ttk widgets."""

from tkinter import font, ttk


FONT_FAMILIES = (
    'Microsoft JhengHei',
    'PingFang TC',
    'Noto Sans CJK TC',
    'Noto Sans TC',
    'Source Han Sans TC',
    'WenQuanYi Micro Hei',
    'Noto Sans CJK SC',
)


def configure_fonts(root):
    available = {name.casefold(): name for name in font.families(root)}
    family = next((available[name.casefold()] for name in FONT_FAMILIES
                   if name.casefold() in available), None)
    if family is not None:
        for name in ('TkDefaultFont', 'TkTextFont', 'TkMenuFont',
                     'TkHeadingFont', 'TkCaptionFont', 'TkSmallCaptionFont',
                     'TkIconFont', 'TkTooltipFont'):
            font.nametofont(name, root=root).configure(family=family)
    # Cover classic Tk controls, combobox popups, and themed widgets.
    root.option_add('*Font', 'TkDefaultFont')
    ttk.Style(root).configure('.', font='TkDefaultFont')
    return family or font.nametofont('TkDefaultFont', root=root).actual('family')
