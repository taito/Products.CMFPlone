from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression
from Products.CMFCore import CMFCorePermissions

__author__ = 'DannyB (ender)'

conversions={'here/about_slot/macros/aboutBox':'',
      'here/calendar_slot/macros/calendarBox':'here/portlet_calendar/macros/portlet',
      'here/events_slot/macros/eventsBox':'here/portlet_events/macros/portlet',
      'here/favorites_slot/macros/favoritesBox':'here/portlet_favorites/macros/portlet',
      'here/language_slot/macros/languageBox':'here/portlet_language/macros/portlet',
      'here/login_slot/macros/loginBox':'here/portlet_login/macros/portlet',
      'here/navigation_tree_slot/macros/navigationBox':'here/portlet_navigation/macros/portlet',
      'here/news_slot/macros/newsBox':'here/portlet_news_/macros/portlet',
      'here/recently_published_slot/macros/recentlyPublishedBox':'here/recently_published_slot/macros/portlet',
      'here/related_slot/macros/relatedBox':'here/portlet_related/macros/portlet',
      'here/workflow_review_slot/macros/review_box':'here/portlet_review/portlet'}

def upgradeSlots2Portlets(portal):
    # traverse all folderish objects and do:
    # if exist: rename right_slots, left_slots to column_two_portlets, column_one_portlets
    # rename slots in these properties use the conversion list above

    # handle current obj first
    processObject(portal)
    processFolderish(portal)

def processFolderish(obj):
    for o in obj.contentValues():
        if o.isPrincipiaFolderish:
            processObject(o)
            processFolderish(o)

def processObject(o):
    left = getattr(o.aq_base, 'left_slots', None)
    #print left
    if left:
        new=renameEntries(left)
        o.left_slots=tuple(new)
        #print o.left_slots
    right = getattr(o.aq_base, 'right_slots', None)
    #print right
    if right:
        new=renameEntries(right)
        o.right_slots=tuple(new)
        #print o.right_slots

def renameEntries(lines):
    new=[]
    for line in lines:
        if conversions.has_key(line):
            if conversions[line]!='':
                new.append(conversions[line])
        else:
            #retain the line
            new.append(line)
    return new
