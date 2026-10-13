from articles.models import AboutAuthorPage, SectionIndexPage, SpecialIssuePage


def nav_sections(request):
    """Feeds the header nav on every page: About Author (always labeled
    'About Author' in the nav, regardless of what its page title is set
    to), then the 4 practice areas, then Special Issue."""
    sections = []

    for page in AboutAuthorPage.objects.live().public():
        page.nav_label = "About Author"
        sections.append(page)

    for page in SectionIndexPage.objects.live().public().order_by("path"):
        page.nav_label = page.title
        sections.append(page)

    for page in SpecialIssuePage.objects.live().public():
        page.nav_label = page.title
        sections.append(page)

    return {"nav_sections": sections}