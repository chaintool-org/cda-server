from dao.models import CdaAddressOperation


async def save_cda_address_operation(cda_address_operation: CdaAddressOperation) -> CdaAddressOperation:
   return await CdaAddressOperation.save(cda_address_operation)
