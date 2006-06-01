## Script (Python) "lookupTypeAction"
##title=Get the target template of an FTI action for the current context
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=actionId
context.plone_log("The lookupTypeAction script is deprecated and will be "
                  "removed in plone 3.5.")

action = None
fti = context.getTypeInfo()

try:
    # XXX: This isn't quite right since it assumeCs the action starts with ${object_url}
    action = fti.getActionInfo(actionId)['url'].split('/')[-1]
except ValueError:
    # If the action doesn't exist, stop
    return None

# Try resolving method aliases
try:
    action = fti.queryMethodID(action, default = action, context = context)
except AttributeError:
    # Don't die if we don't have CMF 1.5
    pass

if action and action[0] == '/':
    action = action[1:]

return action