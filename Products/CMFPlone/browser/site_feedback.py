# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from zope.interface import implements
from zope.component import getMultiAdapter

from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five import BrowserView


class SiteFeedbackView(BrowserView):

    def __call__(self):
        reg_tool = self.context.portal_registration
        putils = self.context.plone_utils
        url = None

        if not 'sender_from_address' in self.request.keys():
            putils.addPortalMessage(_(u'Please submit an email address.'),
                                    'error')
            url = "%s/@@contact-info" % self.context.absolute_url()
        else:
            sender_from_address = self.request['sender_from_address']
            if reg_tool.isValidEmail(sender_from_address):
                pass
            else:
                putils.addPortalMessage(_(u'You entered an invalid email '
                                           'address.'),
                                        'error')
            url = "%s/@@contact-info" % self.context.absolute_url()

        if not ('subject' in self.request.keys() and
           self.request['subject'].strip() == ""):
            putils.addPortalMessage(_(u'Please enter a subject.'),
                                    'error')
            url = "%s/@@contact-info" % self.context.absolute_url()

        if not ('message' in self.request.keys() and
           self.request['message'].strip() == ""):
            putils.addPortalMessage(_(u'Please enter a message'),
                                    'error')
            url = "%s/@@contact-info" % self.context.absolute_url()

        if url:
            return self.request.response.redirect(url)
        else:
            return  self.request.response.redirect(self.context.absolute_url())
