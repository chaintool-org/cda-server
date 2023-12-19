class ReportAddressDTO:
    def __init__(self, organization, address, network, category, confidence, source, entity, is_public, gmt_create,
                 gmt_modified):
        self.org = organization
        self.address = address
        self.network = network
        self.category = category
        self.confidence = confidence
        self.source = source
        self.entity = entity
        self.public = is_public
        self.gmtCreate = gmt_create
        self.gmtModified = gmt_modified


def map_cda_address_report_to_dto(cda_address_report):
    return ReportAddressDTO(
        organization=cda_address_report.organization,
        address=cda_address_report.address,
        network=cda_address_report.network,
        category=cda_address_report.category,
        confidence=cda_address_report.confidence,
        source=cda_address_report.source,
        entity=cda_address_report.entity,
        is_public=cda_address_report.is_public,
        gmt_create=cda_address_report.gmt_create,
        gmt_modified=cda_address_report.gmt_modified,
    )
