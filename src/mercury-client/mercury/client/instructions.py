

def hpssa_clear_configuration_all_controllers():
    return {
        'instruction': 'hpssa_clear_configuration_all_controllers'
    }


def hp_create_array(slot, selection, raid):
    return {
        'instruction': 'hpssa_create_array',
        'kwargs': {
            'slot': slot,
            'selection': selection,
            'raid': raid
        }
    }


def press_preprocessor():
    pass


def disk_query(selection):
    return {
        'query': selection,
    }