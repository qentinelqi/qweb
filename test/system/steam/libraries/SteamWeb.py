from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn


class SteamWeb(object):
    def __init__(self):
        """Initialize library.

        Adds SelectMenu keyword for Steam web pages
        """
        self.QWeb = BuiltIn().get_library_instance('QWeb')

    @keyword
    def steam_menu(self, menu, selection):
        """Selects entry from dropdown menu
        """
        menu_xpath = "//*[text()='%s']" % menu
        self.QWeb.hover_element(menu_xpath)
        self.QWeb.click_text(selection, menu)
