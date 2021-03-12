class Collection(object):

    def __init__(self, type, setup):

        self.product = []
        self.name = type
        self.setup = setup

        self.lid = self.collection_lid()
        self.vid = self.collection_vid()

        return


    def add(self, element):
        
        self.product.append(element)

    def collection_lid(self):

        collection_lid = \
            'urn:nasa:pds:{}.spice:{}'.format(
                    self.setup.mission_accronym,
                    self.type)

        return collection_lid

    def collection_vid(self):

        return '{}.0'.format(int(self.setup.release))


class SpiceKernelsCollection(Collection):

    def __init__(self, setup, bundle):

        self.bundle      = bundle
        self.type        = 'spice_kernels'
        self.start_time  = setup.mission_start
        self.stop_time   = setup.mission_stop

        Collection.__init__(self, self.type, setup)

        return


class DocumentCollection(Collection):

    def __init__(self, setup):

        if setup.pds == '3':
            self.type = 'DOCUMENT'
        elif setup.pds == '4':
            self.type = 'document'

        Collection.__init__(self, self.type, setup)

        return