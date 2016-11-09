from Products.Archetypes.exceptions import ReferenceException

from bika.lims.browser.bika_listing import WorkflowAction
from bika.lims import PMF
from bika.lims.workflow import doActionFor
from bika.sanbi.config import VOLUME_UNITS

import plone

class BiospecimenWorkflowAction(WorkflowAction):

    def __call__(self):
        form = self.request.form
        plone.protect.CheckAuthenticator(form)
        action, _ = WorkflowAction._get_form_workflow_action(self)
        if type(action) in (list, tuple):
            action = action[0]

        # Call out to the workflow action method
        method_name = 'workflow_action_' + action
        method = getattr(self, method_name, False)
        if method:
            method()
        else:
            WorkflowAction.__call__(self)

    def workflow_action_receive(self):
        form = self.request.form
        # print form
        selected_biospecimens = WorkflowAction._get_selected_items(self)
        biospecimens = []
        for uid in selected_biospecimens.keys():
            if not form['Barcode'][0][uid] or \
                    not form['Type'][0][uid] or \
                    not form['Volume'][0][uid] or \
                    not form['Unit'][0][uid] or \
                    not form['SubjectID'][0][uid]:
                continue

            try:
                obj = selected_biospecimens.get(uid, None)
                obj.getField('Barcode').set(obj, form['Barcode'][0][uid])
                obj.getField('SampleType').set(obj, form['Type'][0][uid])
                obj.getField('Volume').set(obj, form['Volume'][0][uid])
                obj.getField('SubjectID').set(obj, form['SubjectID'][0][uid])
                unit = 'ml'
                for u in VOLUME_UNITS:
                    if u['ResultValue'] == form['Unit'][0][uid]:
                        unit = u['ResultText']
                obj.getField('Unit').set(obj, unit)
                obj.reindexObject()
                biospecimens.append(obj)
            except ReferenceException:
                continue

        message = PMF("Changes saved.")
        self.context.plone_utils.addPortalMessage(message, 'info')

        for biospecimen in biospecimens:
            doActionFor(biospecimen, 'receive')
            for partition in biospecimen.objectValues('SamplePartition'):
                doActionFor(partition, 'receive')

        self.destination_url = self.context.absolute_url()
        if self.context.portal_type == 'Project':
            self.destination_url += '/biospecimens'
        self.request.response.redirect(self.destination_url)