from streamlit_option_menu import option_menu # type: ignore
from app_constants import PLACES_INDEXES

def place_selector():
    return option_menu(
            menu_title = '',
            menu_icon = '',
            icons = ['none'] * 4,
            orientation = 'horizontal',
            options = PLACES_INDEXES,
            default_index = 0,
        )