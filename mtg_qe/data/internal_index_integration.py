# Samuel Dunn
# CS 483, Fall 2019

def get_internal_index():
    """
    Returns the 'internal index' for the project.
    The internal index is a pair of dicts that arrange
    card objects in easy-to-use outside of whoosh ways.
    The first dict, keyed by 'by_name', stores cards instances
    with a unique name. The second dict, keyed by 'by_multiverseid',
    stores all cards (all cards scraped) by their multiverseid.
    Between the two, any time we have a result from whoosh and need
    to navigate to another card or print, we should be covered.
    """
    # there's a fun trick to 'hiding', rather obscuring, things in module namespace.
    # namespaces, and instance attributes, ultimately boil down
    # to a dict *somewhere*. With the local module, you can
    # retrieve this dict with the globals() function.
    # If you have a global variable named, say, `foo`, then
    # the globals() dict will have a key in it  "foo".
    # While creating variables requires you to adhere to naming
    # conventions, dict's can be keyed by any hashable (so all strings).
    # This means you can obscure things in the module's namespace by
    # using an illegal variable name (something like, say, "!!my_obscured_var")
    # This makes it impossible to reference the value in a usual way
    # while still being able to access it via that dict.
    # I say 'obscure' instead of 'hide' because anyone who introspects
    # the dict will undoubtedly see its presence, but in my experience
    # it tends to fool IDEs and the like.

    # To compound with this, modules are really just objects.
    # we can store things in that object and trust that its still there
    # so long as the module is alive, or at least not reloaded.
    # this allows us to achieve singleton-like behavior, as a module
    # will typically only be loaded once unless there's some shenanigans afoot.

    # So to ensure that the large internal_index.json file is only parsed once
    # we'll combine these two tools.

    if globals().get('!!_idx_dict', None) == None:
        # load the json file into globals()['!!_idx_dict']
        from . import get_data_location
        from ..model.card import Card
        import os
        import json
        with open(os.path.join(get_data_location(), 'internal_index.json')) as fd:
            deflated_cards = json.load(fd)

        # inflate all cards in the data set.
        inflated_cards = {'by_name': {}, 'by_multiverseid': {}}
        for top_level_key in inflated_cards: # there are non-card fields in internal_index, so iter over inflated_cads
            for key, value in deflated_cards[top_level_key].items():
                inflated_cards[top_level_key][key] = Card().deserialize(value)

        # push the inflated cards into the dict with non-card fields.
        deflated_cards.update(inflated_cards)
        # Set the global value:
        globals()['!!_idx_dict'] = deflated_cards

    return globals().get('!!_idx_dict')