# RFC 1: Provide option to require a comment when submitting content for moderation

* RFC: 1
* Author: Steve Jalim and Val Grimm
* Created: 2015-08-05
* Last Modified: 2015-08-05

## Abstract

Moderators for Wagtail websites do not always have context when content is submitted to them for moderation.
Requiring that a comment be included with each moderation request prompts content contributors to follow an effective coordination workflow. 

## Specification

####AC####
End user behavior: After an Editor (or role with equivalent permissions) selects "Submit for Moderation" in the [?name] dropdown
they should be redirected to a page with a required field with the label
"Please write a comment here to provide context for your submission" of length 150 characters with a
"Confirm submission" button beneath it that is grayed out and un-clickable.
Only after the user has entered content in the field will the button become clickable.

Administration behavior: It should be possible to deactivate this functionality in code. 

The technical specification should describe the syntax and semantics of any new feature.
The specification should be detailed enough to allow implementation -- that is,
developers other than the author should (given the right experience) be able to
independently implement the feature, given only the RFC.

Include subheadings as necessary.

### Sub-headings 1


### Sub-heading n


## Open Questions

// Include any questions until Status is ‘Accepted’
