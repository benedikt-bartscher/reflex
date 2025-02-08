"""Components for displaying the Reflex sticky logo."""

from reflex.components.component import ComponentNamespace
from reflex.components.core.colors import color
from reflex.components.core.cond import color_mode_cond, cond
from reflex.components.core.responsive import tablet_and_desktop
from reflex.components.el.elements.inline import A
from reflex.components.el.elements.media import Path, Rect, Svg
from reflex.components.radix.themes.typography.text import Text
from reflex.experimental.client_state import ClientStateVar
from reflex.style import Style
from reflex.vars.base import Var, VarData


class StickyLogo(Svg):
    """A simple Reflex logo SVG with only the letter R."""

    @classmethod
    def create(cls):
        """Create the simple Reflex logo SVG.

        Returns:
            The simple Reflex logo SVG.
        """
        return super().create(
            Rect.create(width="16", height="16", rx="2", fill="#6E56CF"),
            Path.create(d="M10 9V13H12V9H10Z", fill="white"),
            Path.create(d="M4 3V13H6V9H10V7H6V5H10V7H12V3H4Z", fill="white"),
            width="16",
            height="16",
            viewBox="0 0 16 16",
            xmlns="http://www.w3.org/2000/svg",
        )

    def add_style(self):
        """Add the style to the component.

        Returns:
            The style of the component.
        """
        return Style(
            {
                "fill": "white",
            }
        )


class StickyLabel(Text):
    """A label that displays the Reflex sticky."""

    @classmethod
    def create(cls):
        """Create the sticky label.

        Returns:
            The sticky label.
        """
        return super().create("Built with Reflex")

    def add_style(self):
        """Add the style to the component.

        Returns:
            The style of the component.
        """
        return Style(
            {
                "color": color("slate", 1),
                "font_weight": "600",
                "font_family": "'Instrument Sans', sans-serif",
                "font_size": "0.875rem",
                "line_height": "1rem",
                "letter_spacing": "-0.00656rem",
            }
        )


class StickyBadge(A):
    """A badge that displays the Reflex sticky logo."""

    @classmethod
    def create(cls):
        """Create the sticky badge.

        Returns:
            The sticky badge.
        """
        return super().create(
            StickyLogo.create(),
            tablet_and_desktop(StickyLabel.create()),
            href="https://reflex.dev",
            target="_blank",
            width="auto",
            padding="0.375rem",
            align="center",
            text_align="center",
        )

    def add_style(self):
        """Add the style to the component.

        Returns:
            The style of the component.
        """
        is_localhost_cs = ClientStateVar.create(
            "is_localhost",
            default=True,
            global_ref=False,
        )
        localhost_hostnames = Var.create(["localhost", "127.0.0.1", "[::1]"])
        is_localhost_expr = localhost_hostnames.contains(
            Var("window.location.hostname", _var_type=str).guess_type(),
        )
        check_is_localhost = Var(
            f"useEffect(({is_localhost_cs}) => {is_localhost_cs.set}({is_localhost_expr}), [])",
            _var_data=VarData(
                imports={"react": "useEffect"},
            ),
        )
        is_localhost = is_localhost_cs.value._replace(
            merge_var_data=VarData.merge(
                check_is_localhost._get_all_var_data(),
                VarData(hooks={str(check_is_localhost): None}),
            ),
        )
        return Style(
            {
                "position": "fixed",
                "bottom": "1rem",
                "right": "1rem",
                # Do not show the badge on localhost.
                "display": cond(is_localhost, "none", "flex"),
                "flex-direction": "row",
                "gap": "0.375rem",
                "align-items": "center",
                "width": "auto",
                "border-radius": "0.5rem",
                "color": color_mode_cond("#E5E7EB", "#27282B"),
                "border": color_mode_cond("1px solid #27282B", "1px solid #E5E7EB"),
                "background-color": color_mode_cond("#151618", "#FCFCFD"),
                "padding": "0.375rem",
                "transition": "background-color 0.2s ease-in-out",
                "box-shadow": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
                "z-index": "9998",
                "cursor": "pointer",
            },
        )


class StickyNamespace(ComponentNamespace):
    """Sticky components namespace."""

    __call__ = staticmethod(StickyBadge.create)
    label = staticmethod(StickyLabel.create)
    logo = staticmethod(StickyLogo.create)


sticky = StickyNamespace()
