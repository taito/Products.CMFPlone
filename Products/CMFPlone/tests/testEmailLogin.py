from AccessControl import Unauthorized
from Testing.ZopeTestCase import FunctionalDocFileSuite
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.utils import set_own_login_name
from Products.CMFPlone.RegistrationTool import get_member_by_login_name
from Products.CMFPlone.tests.test_mails import MockMailHostTestCase
from Products.CMFPlone.tests.test_mails import OPTIONFLAGS


class TestEmailLogin(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        pass

    def testUseEmailProperty(self):
        props = getToolByName(self.portal, 'portal_properties').site_properties
        self.assertTrue(props.hasProperty('use_email_as_login'))
        self.assertEqual(props.getProperty('use_email_as_login'), False)

    def testSetOwnLoginName(self):
        memship = self.portal.portal_membership
        users = self.portal.acl_users.source_users
        member = memship.getAuthenticatedMember()
        self.assertEqual(users.getLoginForUserId(PloneTestCase.default_user),
                         PloneTestCase.default_user)
        set_own_login_name(member, 'maurits')
        self.assertEqual(users.getLoginForUserId(PloneTestCase.default_user),
                         'maurits')

    def testSetLoginNameOfOther(self):
        memship = self.portal.portal_membership
        memship.addMember('maurits', 'secret', [], [])
        member = memship.getMemberById('maurits')
        self.assertRaises(Unauthorized, set_own_login_name, member, 'vanrees')
        # The admin *should* be able to change the login name of
        # another user.  See http://dev.plone.org/plone/ticket/11255
        self.loginAsPortalOwner()
        set_own_login_name(member, 'vanrees')
        users = self.portal.acl_users.source_users
        self.assertEqual(users.getLoginForUserId('maurits'), 'vanrees')

    def testAdminSetOwnLoginName(self):
        memship = self.portal.portal_membership
        self.loginAsPortalOwner()
        member = memship.getAuthenticatedMember()
        # We are not allowed to change a user at the root zope level.
        self.assertRaises(KeyError, set_own_login_name, member, 'vanrees')

    def testNormalMemberIdsAllowed(self):
        pattern = self.portal.portal_registration._ALLOWED_MEMBER_ID_PATTERN
        self.assertTrue(pattern.match('maurits'))
        self.assertTrue(pattern.match('Maur1ts'))
        # PLIP9214: the next test actually passes with the original
        # pattern but fails with the new one as email addresses cannot
        # end in a number:
        #self.assertTrue(pattern.match('maurits76'))
        self.assertTrue(pattern.match('MAURITS'))

    def testEmailMemberIdsAllowed(self):
        pattern = self.portal.portal_registration._ALLOWED_MEMBER_ID_PATTERN
        self.assertTrue(pattern.match('user@example.org'))
        self.assertTrue(pattern.match('user123@example.org'))
        self.assertTrue(pattern.match('user.name@example.org'))

    def testIsMemberIdAllowed(self):
        # The standard member id pattern now accepts normal email
        # addresses like above, but it has troubles with some special
        # addresses that are still allowed as email address.  We allow
        # that when use_email_as_login is switched on.
        # See https://dev.plone.org/ticket/11616
        props = getToolByName(self.portal, 'portal_properties').site_properties
        props._updateProperty('use_email_as_login', True)
        registration = getToolByName(self.portal, 'portal_registration')
        self.assertTrue(registration.isMemberIdAllowed('user@example.org'))
        self.assertTrue(registration.isMemberIdAllowed('user+test@example.org'))
        self.assertTrue(registration.isMemberIdAllowed("o'hara@example.org"))
        # Some strange but valid email address will now be allowed,
        # because of the standard pattern:
        self.assertTrue(registration.isMemberIdAllowed("no.address@example"))
        # But those will not validate as email address, so they will
        # be rejected in a different part of the code.
        from Products.CMFPlone.PloneTool import EMAIL_RE
        self.assertFalse(EMAIL_RE.match('no.address@example'))
        # We do still allow normal non-email addresses, just to be
        # sure, because some code might directly call the registration
        # tool.  The standard registration form in the Plone UI will
        # check if an email address is filled in.
        self.assertTrue(registration.isMemberIdAllowed('joe'))

    def test_get_member_by_login_name(self):
        memship = self.portal.portal_membership
        context = self.portal
        member = memship.getMemberById(PloneTestCase.default_user)

        # Login name and user name start out the same
        found = get_member_by_login_name(context, PloneTestCase.default_user)
        self.assertEqual(member, found)

        # Change the login name:
        set_own_login_name(member, 'vanrees')
        # A member with this user name is still returned:
        found = get_member_by_login_name(context, PloneTestCase.default_user)
        self.assertEqual(member, found)
        # With the changed login name we can find the member:
        found = get_member_by_login_name(context, 'vanrees')
        self.assertEqual(member, found)

        # Demonstrate that we can find other members than just the
        # default user:
        found = get_member_by_login_name(context, 'portal_owner')
        member = memship.getMemberById('portal_owner')
        self.assertEqual(member, found)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestEmailLogin))
    # We have some browser tests as well.  Part of that is testing the
    # password reset email, so we borrow some setup from
    # test_mails.py.
    suite.addTest(FunctionalDocFileSuite(
                'emaillogin.txt',
                optionflags=OPTIONFLAGS,
                package='Products.CMFPlone.tests',
                test_class=MockMailHostTestCase))
    return suite
