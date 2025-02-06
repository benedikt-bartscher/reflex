from dataclasses import dataclass
from typing import cast

import pytest

import reflex as rx


class SideBarState(rx.State):
    """State for the side bar."""

    current_page: rx.Field[str] = rx.field("/")


@dataclass(frozen=True)
class SideBarPage:
    """A page in the side bar."""

    title: str
    href: str


@dataclass(frozen=True)
class SideBarSection:
    """A section in the side bar."""

    name: str
    icon: str
    pages: tuple[SideBarPage, ...]


@dataclass(frozen=True)
class Category:
    """A category in the side bar."""

    name: str
    href: str
    sections: tuple[SideBarSection, ...]


SIDE_BAR = (
    Category(
        name="General",
        href="/",
        sections=(
            SideBarSection(
                name="Home",
                icon="home",
                pages=(
                    SideBarPage(title="Home", href="/"),
                    SideBarPage(title="Contact", href="/contact"),
                ),
            ),
            SideBarSection(
                name="About",
                icon="info",
                pages=(
                    SideBarPage(title="About", href="/about"),
                    SideBarPage(title="FAQ", href="/faq"),
                ),
            ),
        ),
    ),
    Category(
        name="Projects",
        href="/projects",
        sections=(
            SideBarSection(
                name="Python",
                icon="worm",
                pages=(
                    SideBarPage(title="Python", href="/projects/python"),
                    SideBarPage(title="Django", href="/projects/django"),
                    SideBarPage(title="Flask", href="/projects/flask"),
                    SideBarPage(title="FastAPI", href="/projects/fastapi"),
                    SideBarPage(title="Pyramid", href="/projects/pyramid"),
                    SideBarPage(title="Tornado", href="/projects/tornado"),
                    SideBarPage(title="TurboGears", href="/projects/turbogears"),
                    SideBarPage(title="Web2py", href="/projects/web2py"),
                    SideBarPage(title="Zope", href="/projects/zope"),
                    SideBarPage(title="Plone", href="/projects/plone"),
                    SideBarPage(title="Quixote", href="/projects/quixote"),
                    SideBarPage(title="Bottle", href="/projects/bottle"),
                    SideBarPage(title="CherryPy", href="/projects/cherrypy"),
                    SideBarPage(title="Falcon", href="/projects/falcon"),
                    SideBarPage(title="Sanic", href="/projects/sanic"),
                    SideBarPage(title="Starlette", href="/projects/starlette"),
                ),
            ),
            SideBarSection(
                name="JavaScript",
                icon="banana",
                pages=(
                    SideBarPage(title="JavaScript", href="/projects/javascript"),
                    SideBarPage(title="Angular", href="/projects/angular"),
                    SideBarPage(title="React", href="/projects/react"),
                    SideBarPage(title="Vue", href="/projects/vue"),
                    SideBarPage(title="Ember", href="/projects/ember"),
                    SideBarPage(title="Backbone", href="/projects/backbone"),
                    SideBarPage(title="Meteor", href="/projects/meteor"),
                    SideBarPage(title="Svelte", href="/projects/svelte"),
                    SideBarPage(title="Preact", href="/projects/preact"),
                    SideBarPage(title="Mithril", href="/projects/mithril"),
                    SideBarPage(title="Aurelia", href="/projects/aurelia"),
                    SideBarPage(title="Polymer", href="/projects/polymer"),
                    SideBarPage(title="Knockout", href="/projects/knockout"),
                    SideBarPage(title="Dojo", href="/projects/dojo"),
                    SideBarPage(title="Riot", href="/projects/riot"),
                    SideBarPage(title="Alpine", href="/projects/alpine"),
                    SideBarPage(title="Stimulus", href="/projects/stimulus"),
                    SideBarPage(title="Marko", href="/projects/marko"),
                    SideBarPage(title="Sapper", href="/projects/sapper"),
                    SideBarPage(title="Nuxt", href="/projects/nuxt"),
                    SideBarPage(title="Next", href="/projects/next"),
                    SideBarPage(title="Gatsby", href="/projects/gatsby"),
                    SideBarPage(title="Gridsome", href="/projects/gridsome"),
                    SideBarPage(title="Nest", href="/projects/nest"),
                    SideBarPage(title="Express", href="/projects/express"),
                    SideBarPage(title="Koa", href="/projects/koa"),
                    SideBarPage(title="Hapi", href="/projects/hapi"),
                    SideBarPage(title="LoopBack", href="/projects/loopback"),
                    SideBarPage(title="Feathers", href="/projects/feathers"),
                    SideBarPage(title="Sails", href="/projects/sails"),
                    SideBarPage(title="Adonis", href="/projects/adonis"),
                    SideBarPage(title="Meteor", href="/projects/meteor"),
                    SideBarPage(title="Derby", href="/projects/derby"),
                    SideBarPage(title="Socket.IO", href="/projects/socketio"),
                ),
            ),
        ),
    ),
)


def side_bar_page(page: SideBarPage):
    return rx.box(
        rx.link(
            page.title,
            href=page.href,
        )
    )


def side_bar_section(section: SideBarSection):
    return rx.accordion.item(
        rx.accordion.header(
            rx.accordion.trigger(
                rx.hstack(
                    rx.hstack(
                        rx.icon(section.icon),
                        section.name,
                        align="center",
                    ),
                    rx.accordion.icon(),
                    width="100%",
                    justify="between",
                )
            )
        ),
        rx.accordion.content(
            rx.vstack(
                *map(side_bar_page, section.pages),
            ),
            border_inline_start="1px solid",
            padding_inline_start="1em",
            margin_inline_start="1.5em",
        ),
        value=section.name,
        width="100%",
        variant="ghost",
    )


def side_bar_category(category: Category):
    selected_section = cast(
        rx.Var,
        rx.match(
            SideBarState.current_page,
            *[
                (
                    section.name,
                    section.name,
                )
                for section in category.sections
            ],
            None,
        ),
    )
    return rx.vstack(
        rx.heading(
            rx.link(
                category.name,
                href=category.href,
            ),
            size="5",
        ),
        rx.accordion.root(
            *map(side_bar_section, category.sections),
            default_value=selected_section.to(str),
            variant="ghost",
            width="100%",
            collapsible=True,
            type="multiple",
        ),
        width="100%",
    )


def side_bar():
    return rx.vstack(
        *map(side_bar_category, SIDE_BAR),
        width="fit-content",
    )


LOREM_IPSUM = "Lorem ipsum dolor sit amet, dolor ut dolore pariatur aliqua enim tempor sed. Labore excepteur sed exercitation. Ullamco aliquip lorem sunt enim in incididunt. Magna anim officia sint cillum labore. Ut eu non dolore minim nostrud magna eu, aute ex in incididunt irure eu. Fugiat et magna magna est excepteur eiusmod minim. Quis eiusmod et non pariatur dolor veniam incididunt, eiusmod irure enim sed dolor lorem pariatur do. Occaecat duis irure excepteur dolore. Proident ut laborum pariatur sit sit, nisi nostrud voluptate magna commodo laborum esse velit. Voluptate non minim deserunt adipiscing irure deserunt cupidatat. Laboris veniam commodo incididunt veniam lorem occaecat, fugiat ipsum dolor cupidatat. Ea officia sed eu excepteur culpa adipiscing, tempor consectetur ullamco eu. Anim ex proident nulla sunt culpa, voluptate veniam proident est adipiscing sint elit velit. Laboris adipiscing est culpa cillum magna. Sit veniam nulla nulla, aliqua eiusmod commodo lorem cupidatat commodo occaecat. Fugiat cillum dolor incididunt mollit eiusmod sint. Non lorem dolore labore excepteur minim laborum sed. Irure nisi do lorem nulla sunt commodo, deserunt quis mollit consectetur minim et esse est, proident nostrud officia enim sed reprehenderit. Magna cillum consequat aute reprehenderit duis sunt ullamco. Labore qui mollit voluptate. Duis dolor sint aute amet aliquip officia, est non mollit tempor enim quis fugiat, eu do culpa consectetur magna. Do ullamco aliqua voluptate culpa excepteur reprehenderit reprehenderit. Occaecat nulla sit est magna. Deserunt ea voluptate veniam cillum. Amet cupidatat duis est tempor fugiat ex eu, officia est sunt consectetur labore esse exercitation. Nisi cupidatat irure est nisi. Officia amet eu veniam reprehenderit. In amet incididunt tempor commodo ea labore. Mollit dolor aliquip excepteur, voluptate aute occaecat id officia proident. Ullamco est amet tempor. Proident aliquip proident mollit do aliquip ipsum, culpa quis aute id irure. Velit excepteur cillum cillum ut cupidatat. Occaecat qui elit esse nulla minim. Consequat velit id ad pariatur tempor. Eiusmod deserunt aliqua ex sed quis non. Dolor sint commodo ex in deserunt nostrud excepteur, pariatur ex aliqua anim adipiscing amet proident. Laboris eu laborum magna lorem ipsum fugiat velit."


def _simple_page():
    return rx.box(
        rx.heading("Simple Page", size="1"),
        rx.text(LOREM_IPSUM),
    )


def _complicated_page():
    return rx.hstack(
        side_bar(),
        rx.box(
            rx.heading("Complicated Page", size="1"),
            rx.text(LOREM_IPSUM),
        ),
    )


@pytest.fixture(params=[_simple_page, _complicated_page])
def evaluated_page(request):
    return request.param()
