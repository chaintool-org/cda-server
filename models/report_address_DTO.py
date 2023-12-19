class ReportAddressDTO:
    def __init__(self, organization, operate_id, address, network, category, confidence, source, entity, is_public,gmt_create,gmt_modified,id):
        self.org = organization
        self.operate_id = operate_id
        self.address = address
        self.network = network
        self.category = category
        self.confidence = confidence
        self.source = source
        self.entity = entity
        self.is_public = is_public
        self.gmt_create = gmt_create
        self.gmt_modified = gmt_modified
        self.id = id


def map_cda_address_report_to_dto(cda_address_report):
    return ReportAddressDTO(
        organization=cda_address_report.organization,
        operate_id=cda_address_report.operate_id,
        address=cda_address_report.address,
        network=cda_address_report.network,
        category=cda_address_report.category,
        confidence=cda_address_report.confidence,
        source=cda_address_report.source,
        entity=cda_address_report.entity,
        is_public=cda_address_report.is_public,
        gmt_create=cda_address_report.gmt_create,
        gmt_modified=cda_address_report.gmt_modified,
        id=cda_address_report.id
    )
