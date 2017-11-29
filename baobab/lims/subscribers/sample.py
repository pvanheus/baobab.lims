from zope.interface import alsoProvides
from Products.Five.utilities.marker import erase
from bika.lims.workflow import doActionFor
from baobab.lims.interfaces import ISharableSample
from baobab.lims.browser.project import create_samplepartition


def ObjectInitializedEventHandler(instance, event):
    """called an object is created
    """
    if instance.portal_type == 'Sample':

        if instance.getField('AllowSharing').get(instance):
            alsoProvides(instance, ISharableSample)
            instance.reindexObject()

        if not instance.getField('Barcode').get(instance):
            instance.getField('Barcode').set(instance, instance.getId())

        create_samplepartition(instance, {'services': [], 'part_id': instance.getId() + "-P"})

        if float(instance.getField('Volume').get(instance)) > 0:
            doActionFor(instance, 'sample_due')
            doActionFor(instance, 'receive')

        location = instance.getStorageLocation()
        if location:
            doActionFor(location, 'occupy')
            instance.update_box_status(location)


def ObjectModifiedEventHandler(instance, event):
    """ Called if the object is modified
    """
    if instance.portal_type == 'Sample':

        if not ISharableSample.providedBy(instance) and \
                instance.getField('AllowSharing').get(instance):
            alsoProvides(instance, ISharableSample)
            instance.reindexObject()

        if ISharableSample.providedBy(instance) and \
            not instance.getField('AllowSharing').get(instance):
            erase(instance, ISharableSample)
            instance.reindexObject()

        if not instance.getField('Barcode').get(instance):
            instance.getField('Barcode').set(instance, instance.getId())

        if instance.getField('Barcode').get(instance) != instance.getId():
            instance.setId(instance.getField('Barcode').get(instance))

