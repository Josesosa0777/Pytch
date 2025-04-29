# -*- dataeval: init -*-

import search_systemstate

class Search(search_systemstate.Search):
    sgs = [
        { # FLR20, ARS430 combined endurance run
            "AEBSState": ("AEBS1_2A", "AEBS1_AEBSState_2A_C3")
        },
    ]