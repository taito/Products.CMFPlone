from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zExceptions import NotFound
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five import BrowserView

class ContentAuthor(BrowserView):
    """ """
    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(ContentAuthor, self).__init__(context, request)
        self.author = None

    def publishTraverse(self, request, name):
        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.getMemberById(name) is not None:
            self.author = name
        else:
            raise NotFound(_("No registered user: '%s'" % name))
        return self
