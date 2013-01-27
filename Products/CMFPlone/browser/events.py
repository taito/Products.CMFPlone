from Products.Five import BrowserView

class EventsListingView(BrowserView):
    """ """

    def results(self):
        state = self.context.unrestrictedTraverse('@@plone_portal_state')
        path = state.navigation_root_path()
        results = self.context.portal_catalog.searchResults(
                        dict(
                            portal_type='Event',
                            end={'query': self.context.ZopeTime(),
                                'range': 'min'},
                            sort_on='start',
                            review_state='published',
                            path=path)
                        )
        return results
