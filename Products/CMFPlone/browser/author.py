import logging
from smtplib import SMTPException
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zExceptions import NotFound
 
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.utils import transaction_note
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

log = logging.getLogger(__name__)

class ContentAuthor(BrowserView):
    """ """
    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(ContentAuthor, self).__init__(context, request)
        self.author = None
        self.errors = {}

    def __call__(self):
        if self.author is None:
            raise NotFound
        if self.request.form.get('form.button.Send'):
            self.validate()
            if not self.errors:
                self.send_feedback()
        return self.index()

    def publishTraverse(self, request, name):
        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.getMemberById(name) is not None:
            self.author = name
        else:
            raise NotFound(_("No registered user: '%s'" % name))
        return self

    def validate(self):
        form = self.request.form
        subject = form.get('subject')
        message = form.get('message')
        if not (subject and subject.strip()):
            self.errors['subject'] = \
                    _('subject_required', u'Please enter a subject.')
        if not (message and message.strip()):
            self.errors['message'] = \
                    _('message_required', u'Please enter a message.')
        if self.errors:
            messages = IStatusMessage(self.request)
            messages.add(_(u'Please correct the indicated errors.'), "error")

    def send_feedback(self):
        context = self.context
        request = self.request
        urltool = getToolByName(context, 'portal_url')
        portal = urltool.getPortalObject()
        mtool = getToolByName(context, 'portal_membership')
        sender = mtool.getAuthenticatedMember()
        send_to_address = mtool.getMemberById(self.author).getProperty('email')
        plone_utils = getToolByName(context, 'plone_utils')
         
        send_from_address = sender.getProperty('email')
        if send_from_address == '':
            # happens if you don't exist as user in the portal (but at a higher level)
            # or if your memberdata is incomplete.
            # Would be nicer to check in the feedback form, but that's hard to do
            # securely
            plone_utils.addPortalMessage(_(u'Could not find a valid email address'),
                                        'error')
            return

        sender_id = "%s (%s), %s" % (sender.getProperty('fullname'), sender.getId(),
                                    send_from_address)
        host = context.MailHost  # plone_utils.getMailHost() (is private)
        encoding = portal.getProperty('email_charset')
        ## make these arguments?
        referer = request.get('referer', 'unknown referer')
        subject = request.get('subject', '')
        message = request.get('message', '')
        ## TODO:
        ## Add fullname, memberid to sender
        variables = {'send_from_address' : send_from_address,
                    'sender_id'         : sender_id,
                    'url'               : referer,
                    'subject'           : subject,
                    'message'           : message,
                    'encoding'          : encoding,
                    }

        pmessage = IStatusMessage(self.request)
        try:
            message = context.author_feedback_template(context, **variables)
            message = message.encode(encoding)
            envelope_from = portal.getProperty('email_from_address')
            result = host.send(message, send_to_address, envelope_from,
                            subject=subject, charset=encoding)
        except (SMTPException, RuntimeError) , e:  
            log.error(e)
            exception = plone_utils.exceptionString()
            message = _(u'Unable to send mail: ${exception}',
                        mapping={u'exception': exception})
            pmessage.add(message, 'error')
            return

        tmsg = 'Sent feedback from %s to %s' % ('x', 'y')
        transaction_note(tmsg)
        ## clear request variables so form is cleared as well
        request.set('message', None)
        request.set('subject', None)
        pmessage.add(_(u'Mail sent.'))

