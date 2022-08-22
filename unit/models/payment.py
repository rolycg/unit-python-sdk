from unit.models import *
from unit.utils import date_utils

PaymentTypes = Literal["AchPayment", "BookPayment", "WirePayment", "BillPayment"]
PaymentDirections = Literal["Debit", "Credit"]
PaymentStatus = Literal["Pending", "Rejected", "Clearing", "Sent", "Canceled", "Returned"]
RecurringStatus = Literal["Active", "Completed", "Disabled"]


class Schedule(UnitDTO):
    def __init__(self, start_time: datetime, end_time: datetime, day_of_month: int, interval: str,
                 next_scheduled_action: str, total_number_of_payments: int):
        self.start_time = start_time
        self.end_time = end_time
        self.day_of_month = day_of_month
        self.interval = interval
        self.next_scheduled_action = next_scheduled_action
        self.total_number_of_payments = total_number_of_payments

    @staticmethod
    def from_json_api(data: Dict):
        return Schedule(date_utils.to_date(data["startTime"]), date_utils.to_date(data.get("endTime")),
                        data.get("dayOfMonth"), data["interval"], data["nextScheduledAction"],
                        data.get("totalNumberOfPayments"))


class CreateSchedule(UnitDTO):
    def __init__(self, interval: str, day_of_month: int, start_time: Optional[datetime] = None,
                 end_time: Optional[datetime] = None, total_number_of_payments: Optional[int] = None):
        self.start_time = start_time
        self.end_time = end_time
        self.day_of_month = day_of_month
        self.interval = interval
        self.total_number_of_payments = total_number_of_payments


class BasePayment(object):
    def __init__(self, id: str, created_at: datetime, status: PaymentStatus, direction: PaymentDirections, description: str,
                 amount: int, reason: Optional[str], tags: Optional[Dict[str, str]],
                 relationships: Optional[Dict[str, Relationship]]):
        self.id = id
        self.attributes = {"createdAt": created_at, "status": status, "direction": direction,
                           "description": description, "amount": amount, "reason": reason, "tags": tags}
        self.relationships = relationships


class AchPaymentDTO(BasePayment):
    def __init__(self, id: str, created_at: datetime, status: PaymentStatus, counterparty: Counterparty, direction: str,
                 description: str, amount: int, addenda: Optional[str], reason: Optional[str],
                 settlement_date: Optional[datetime], tags: Optional[Dict[str, str]],
                 relationships: Optional[Dict[str, Relationship]]):
        BasePayment.__init__(self, id, created_at, status, direction, description, amount, reason, tags, relationships)
        self.type = 'achPayment'
        self.attributes["counterparty"] = counterparty
        self.attributes["addenda"] = addenda
        self.settlement_date = settlement_date

    @staticmethod
    def from_json_api(_id, _type, attributes, relationships):
        settlement_date = date_utils.to_date(attributes.get("settlementDate")) if attributes.get("settlementDate") else None
        return AchPaymentDTO(_id, date_utils.to_datetime(attributes["createdAt"]), attributes["status"],
                             Counterparty.from_json_api(attributes["counterparty"]), attributes["direction"], attributes["description"],
                             attributes["amount"], attributes.get("addenda"), attributes.get("reason"), settlement_date,
                             attributes.get("tags"), relationships)

class BookPaymentDTO(BasePayment):
    def __init__(self, id: str, created_at: datetime, status: PaymentStatus, direction: Optional[str], description: str,
                 amount: int, reason: Optional[str], tags: Optional[Dict[str, str]],
                 relationships: Optional[Dict[str, Relationship]]):
        BasePayment.__init__(self, id, created_at, status, direction, description, amount, reason, tags, relationships)
        self.type = 'bookPayment'

    @staticmethod
    def from_json_api(_id, _type, attributes, relationships):
        return BookPaymentDTO(_id, date_utils.to_datetime(attributes["createdAt"]), attributes["status"],
                              attributes.get("direction"), attributes["description"], attributes["amount"],
                              attributes.get("reason"), attributes.get("tags"), relationships)

class WirePaymentDTO(BasePayment):
    def __init__(self, id: str, created_at: datetime, status: PaymentStatus, counterparty: WireCounterparty,
                 direction: str, description: str, amount: int, reason: Optional[str], tags: Optional[Dict[str, str]],
                 relationships: Optional[Dict[str, Relationship]]):
        BasePayment.__init__(self, id, created_at, direction, description, amount, reason, tags, relationships)
        self.type = "wirePayment"
        self.attributes["counterparty"] = counterparty

    @staticmethod
    def from_json_api(_id, _type, attributes, relationships):
        return WirePaymentDTO(_id, date_utils.to_datetime(attributes["createdAt"]), attributes["status"],
                              WireCounterparty.from_json_api(attributes["counterparty"]), attributes["direction"],
                              attributes["description"], attributes["amount"], attributes.get("reason"),
                              attributes.get("tags"), relationships)

class BillPaymentDTO(BasePayment):
    def __init__(self, id: str, created_at: datetime, status: PaymentStatus, direction: str, description: str,
                 amount: int, tags: Optional[Dict[str, str]], relationships: Optional[Dict[str, Relationship]]):
        BasePayment.__init__(self, id, created_at, status, direction, description, amount, reason, tags, relationships)
        self.type = 'billPayment'

    @staticmethod
    def from_json_api(_id, _type, attributes, relationships):
        return BillPaymentDTO(_id, date_utils.to_datetime(attributes["createdAt"]), attributes["status"],
                              attributes["direction"], attributes["description"], attributes["amount"],
                              attributes.get("reason"), attributes.get("tags"), relationships)

PaymentDTO = Union[AchPaymentDTO, BookPaymentDTO, WirePaymentDTO, BillPaymentDTO]

AchReceivedPaymentStatus = Literal["Pending", "Advanced", "Completed", "Returned"]

class AchReceivedPaymentDTO(object):
    def __init__(self, id: str, created_at: datetime, status: AchReceivedPaymentStatus, was_advanced: bool,
                 completion_date: datetime, return_reason: Optional[str], amount: int, description: str,
                 addenda: Optional[str], company_name: str, counterparty_routing_number: str, trace_number: str,
                 sec_code: Optional[str], tags: Optional[Dict[str, str]], relationships: Optional[Dict[str, Relationship]]):
        self.type = "achReceivedPayment"
        self.attributes = {"createdAt": created_at, "status": status, "wasAdvanced": was_advanced,
                           "completionDate": completion_date, "returnReason": return_reason, "description": description,
                           "amount": amount, "addenda": addenda, "companyName": company_name,
                           "counterpartyRoutingNumber": counterparty_routing_number, "traceNumber": trace_number,
                           "secCode": sec_code, "tags": tags}
        self.relationships = relationships

    @staticmethod
    def from_json_api(_id, _type, attributes, relationships):
        return AchReceivedPaymentDTO(_id, date_utils.to_datetime(attributes["createdAt"]), attributes["status"],
                                     attributes["wasAdvanced"], attributes["completionDate"],
                                     attributes.get("returnReason"),attributes["amount"], attributes["description"],
                                     attributes.get("addenda"), attributes.get("companyName"),
                                     attributes.get("counterpartyRoutingNumber"), attributes.get("traceNumber"),
                                     attributes.get("secCode"), attributes.get("tags"), relationships)

class RecurringCreditAchPaymentDTO(object):
    def __init__(self, _id: str, created_at: datetime, update_at: datetime, amount: int, description: str,
                 addenda: Optional[str], status: RecurringStatus, number_of_payments: int, schedule: Schedule,
                 tags: Optional[Dict[str, str]], relationships: Optional[Dict[str, Relationship]]):
        self.id = _id
        self.type = "recurringCreditAchPayment"
        self.attributes = {"createdAt": created_at, "updatedAt": update_at, "amount": amount,
                           "description": description, "addenda": addenda, "status": status,
                           "numberOfPayments": number_of_payments, "schedule": schedule, "tags": tags}
        self.relationships = relationships

    @staticmethod
    def from_json_api(_id, _type, attributes, relationships):
        return RecurringCreditAchPaymentDTO(_id, date_utils.to_datetime(attributes["createdAt"]),
                                            date_utils.to_datetime(attributes["updatedAt"]), attributes["amount"],
                                            attributes["description"], attributes.get("addenda"), attributes["status"],
                                            attributes["numberOfPayments"],
                                            Schedule.from_json_api(attributes["schedule"]), attributes.get("tags"),
                                            relationships)


class RecurringCreditBookPaymentDTO(object):
    def __init__(self, _id: str, created_at: datetime, update_at: datetime, amount: int, description: str,
                 addenda: Optional[str], status: RecurringStatus, number_of_payments: int, schedule: Schedule,
                 tags: Optional[Dict[str, str]], relationships: Optional[Dict[str, Relationship]]):
        self.id = _id
        self.type = "recurringCreditBookPayment"
        self.attributes = {"createdAt": created_at, "updatedAt": update_at, "amount": amount,
                           "description": description, "addenda": addenda, "status": status,
                           "numberOfPayments": number_of_payments, "schedule": schedule, "tags": tags}
        self.relationships = relationships

    @staticmethod
    def from_json_api(_id, _type, attributes, relationships):
        return RecurringCreditBookPaymentDTO(_id, date_utils.to_datetime(attributes["createdAt"]),
                                            date_utils.to_datetime(attributes["updatedAt"]), attributes["amount"],
                                            attributes["description"], attributes.get("addenda"), attributes["status"],
                                            attributes["numberOfPayments"],
                                            Schedule.from_json_api(attributes["schedule"]), attributes.get("tags"),
                                            relationships)


class RecurringCreditAchPaymentDTO(object):
    def __init__(self, _id: str, created_at: datetime, update_at: datetime, amount: int, description: str,
                 addenda: Optional[str], status: RecurringStatus, number_of_payments: int, schedule: Schedule,
                 tags: Optional[Dict[str, str]], relationships: Optional[Dict[str, Relationship]]):
        self.id = _id
        self.type = "recurringCreditAchPayment"
        self.attributes = {"createdAt": created_at, "updatedAt": update_at, "amount": amount,
                           "description": description, "addenda": addenda, "status": status,
                           "numberOfPayments": number_of_payments, "schedule": schedule, "tags": tags}
        self.relationships = relationships

    @staticmethod
    def from_json_api(_id, _type, attributes, relationships):
        return RecurringCreditAchPaymentDTO(_id, date_utils.to_datetime(attributes["createdAt"]),
                                            date_utils.to_datetime(attributes["updatedAt"]), attributes["amount"],
                                            attributes["description"], attributes.get("addenda"), attributes["status"],
                                            attributes["numberOfPayments"],
                                            Schedule.from_json_api(attributes["schedule"]), attributes.get("tags"),
                                            relationships)


RecurringCreditPaymentDTO = Union[RecurringCreditAchPaymentDTO, RecurringCreditBookPaymentDTO]


class CreateRecurringCreditAchPaymentRequest(UnitRequest):
    def __init__(self, amount: int, description: str, relationships: Dict[str, Relationship],
                 idempotency_key: Optional[str], tags: Optional[Dict[str, str]], direction: str = "Credit",
                 type: str = "achPayment"):
        self.type = type
        self.amount = amount
        self.description = description
        self.direction = direction
        self.idempotency_key = idempotency_key
        self.tags = tags
        self.relationships = relationships

    def to_json_api(self) -> Dict:
        payload = {
            "data": {
                "type": self.type,
                "attributes": {
                    "amount": self.amount,
                    "direction": self.direction,
                    "description": self.description
                },
                "relationships": self.relationships
            }
        }

        if self.idempotency_key:
            payload["data"]["attributes"]["idempotencyKey"] = self.idempotency_key

        if self.tags:
            payload["data"]["attributes"]["tags"] = self.tags

        return payload

    def __repr__(self):
        json.dumps(self.to_json_api())


class CreateRecurringCreditPaymentBaseRequest(UnitRequest):
    def __init__(self, amount: int, description: str, schedule: CreateSchedule, relationships: Dict[str, Relationship],
                 idempotency_key: Optional[str], tags: Optional[Dict[str, str]],
                 _type: str = "recurringCreditAchPayment"):
        self.type = _type
        self.amount = amount
        self.description = description
        self.schedule = schedule
        self.idempotency_key = idempotency_key
        self.tags = tags
        self.relationships = relationships

    def to_json_api(self) -> Dict:
        payload = {
            "data": {
                "type": self.type,
                "attributes": {
                    "amount": self.amount,
                    "description": self.description,
                    "schedule": self.schedule
                },
                "relationships": self.relationships
            }
        }

        if self.idempotency_key:
            payload["data"]["attributes"]["idempotencyKey"] = self.idempotency_key

        if self.tags:
            payload["data"]["attributes"]["tags"] = self.tags

        return payload

    def __repr__(self):
        json.dumps(self.to_json_api())


class CreateRecurringCreditAchPaymentRequest(CreateRecurringCreditPaymentBaseRequest):
    def __init__(self, amount: int, description: str, schedule: CreateSchedule, relationships: Dict[str, Relationship],
                 addenda: Optional[str] = None, idempotency_key: Optional[str] = None,
                 tags: Optional[Dict[str, str]] = None):
        CreateRecurringCreditPaymentBaseRequest.__init__(self, amount, description, schedule, relationships,
                                                         idempotency_key, tags)
        self.addenda = addenda

    def to_json_api(self) -> Dict:
        payload = CreateRecurringCreditPaymentBaseRequest.to_json_api(self)

        if self.addenda:
            payload["data"]["attributes"]["addenda"] = self.addenda

        return payload


class CreateRecurringCreditBookPaymentRequest(CreateRecurringCreditPaymentBaseRequest):
    def __init__(self, amount: int, description: str, schedule: CreateSchedule, relationships: Dict[str, Relationship],
                 transaction_summary_override: Optional[str] = None, idempotency_key: Optional[str] = None,
                 tags: Optional[Dict[str, str]] = None):
        CreateRecurringCreditPaymentBaseRequest.__init__(self, amount, description, schedule, relationships,
                                                         idempotency_key, tags, "recurringCreditBookPayment")
        self.transaction_summary_override = transaction_summary_override

    def to_json_api(self) -> Dict:
        payload = CreateRecurringCreditPaymentBaseRequest.to_json_api(self)

        if self.transaction_summary_override:
            payload["data"]["attributes"]["transactionSummaryOverride"] = self.transaction_summary_override

        return payload


CreateRecurringCreditPaymentRequest = Union[CreateRecurringCreditAchPaymentRequest,
                                            CreateRecurringCreditBookPaymentRequest]


class CreatePaymentBaseRequest(UnitRequest):
    def __init__(self, amount: int, description: str, relationships: Dict[str, Relationship],
                 idempotency_key: Optional[str], tags: Optional[Dict[str, str]], direction: str = "Credit",
                 type: str = "achPayment"):
        self.type = type
        self.amount = amount
        self.description = description
        self.direction = direction
        self.idempotency_key = idempotency_key
        self.tags = tags
        self.relationships = relationships

    def to_json_api(self) -> Dict:
        payload = {
            "data": {
                "type": self.type,
                "attributes": {
                    "amount": self.amount,
                    "direction": self.direction,
                    "description": self.description
                },
                "relationships": self.relationships
            }
        }

        if self.idempotency_key:
            payload["data"]["attributes"]["idempotencyKey"] = self.idempotency_key

        if self.tags:
            payload["data"]["attributes"]["tags"] = self.tags

        return payload

    def __repr__(self):
        json.dumps(self.to_json_api())

class CreateInlinePaymentRequest(CreatePaymentBaseRequest):
    def __init__(self, amount: int, description: str, counterparty: Counterparty, relationships: Dict[str, Relationship],
                 addenda: Optional[str], idempotency_key: Optional[str], tags: Optional[Dict[str, str]],
                 direction: str = "Credit"):
        CreatePaymentBaseRequest.__init__(self, amount, description, relationships, idempotency_key, tags, direction)
        self.counterparty = counterparty
        self.addenda = addenda

    def to_json_api(self) -> Dict:
        payload = CreatePaymentBaseRequest.to_json_api(self)

        payload["data"]["attributes"]["counterparty"] = self.counterparty

        if self.addenda:
            payload["data"]["attributes"]["addenda"] = self.addenda

        return payload

class CreateLinkedPaymentRequest(CreatePaymentBaseRequest):
    def __init__(self, amount: int, description: str, relationships: Dict[str, Relationship], addenda: Optional[str],
                 verify_counterparty_balance: Optional[bool], idempotency_key: Optional[str],
                 tags: Optional[Dict[str, str]], direction: str = "Credit"):
        CreatePaymentBaseRequest.__init__(self, amount, description, relationships, idempotency_key, tags, direction)
        self.addenda = addenda
        self.verify_counterparty_balance = verify_counterparty_balance

    def to_json_api(self) -> Dict:
        payload = CreatePaymentBaseRequest.to_json_api(self)

        if self.addenda:
            payload["data"]["attributes"]["addenda"] = self.addenda

        if self.verify_counterparty_balance:
            payload["data"]["attributes"]["verifyCounterpartyBalance"] = self.verify_counterparty_balance

        return payload

class CreateVerifiedPaymentRequest(CreatePaymentBaseRequest):
    def __init__(self, amount: int, description: str, plaid_processor_token: str, relationships: Dict[str, Relationship],
                 counterparty_name: Optional[str], verify_counterparty_balance: Optional[bool],
                 idempotency_key: Optional[str], tags: Optional[Dict[str, str]], direction: str = "Credit"):
        CreatePaymentBaseRequest.__init__(self, amount, description, relationships, idempotency_key, tags)
        self.plaid_Processor_token = plaid_processor_token
        self.counterparty_name = counterparty_name
        self.verify_counterparty_balance = verify_counterparty_balance

    def to_json_api(self) -> Dict:
        payload = CreatePaymentBaseRequest.to_json_api(self)
        payload["data"]["attributes"]["counterparty"] = self.counterparty
        payload["data"]["attributes"]["plaidProcessorToken"] = self.plaid_processor_token

        if self.counterparty_name:
            payload["data"]["attributes"]["counterpartyName"] = self.counterparty_name

        if self.verify_counterparty_balance:
            payload["data"]["attributes"]["verifyCounterpartyBalance"] = self.verify_counterparty_balance

        return payload

class CreateBookPaymentRequest(CreatePaymentBaseRequest):
    def __init__(self, amount: int, description: str, relationships: Dict[str, Relationship],
                 idempotency_key: Optional[str] = None, tags: Optional[Dict[str, str]] = None,
                 direction: str = "Credit"):
        super().__init__(amount, description, relationships, idempotency_key, tags, direction, "bookPayment")

class CreateWirePaymentRequest(CreatePaymentBaseRequest):
    def __init__(self, amount: int, description: str, counterparty: WireCounterparty,
                 relationships: Dict[str, Relationship], idempotency_key: Optional[str], tags: Optional[Dict[str, str]],
                 direction: str = "Credit"):
        CreatePaymentBaseRequest.__init__(self, amount, description, relationships, idempotency_key, tags, direction,
                                      "wirePayment")
        self.counterparty = counterparty

    def to_json_api(self) -> Dict:
        payload = CreatePaymentBaseRequest.to_json_api(self)
        payload["data"]["attributes"]["counterparty"] = self.counterparty
        return payload

CreatePaymentRequest = Union[CreateInlinePaymentRequest, CreateLinkedPaymentRequest, CreateVerifiedPaymentRequest,
                             CreateBookPaymentRequest, CreateWirePaymentRequest]

class PatchAchPaymentRequest(object):
    def __init__(self, payment_id: str, tags: Dict[str, str]):
        self.payment_id = payment_id
        self.tags = tags

    def to_json_api(self) -> Dict:
        payload = {
            "data": {
                "type": "achPayment",
                "attributes": {
                    "tags": self.tags
                }
            }
        }

        return payload

    def __repr__(self):
        json.dumps(self.to_json_api())

class PatchBookPaymentRequest(object):
    def __init__(self, payment_id: str, tags: Dict[str, str]):
        self.payment_id = payment_id
        self.tags = tags

    def to_json_api(self) -> Dict:
        payload = {
            "data": {
                "type": "bookPayment",
                "attributes": {
                    "tags": self.tags
                }
            }
        }

        return payload

    def __repr__(self):
        json.dumps(self.to_json_api())

PatchPaymentRequest = Union[PatchAchPaymentRequest, PatchBookPaymentRequest]

class ListPaymentParams(UnitParams):
    def __init__(self, limit: int = 100, offset: int = 0, account_id: Optional[str] = None,
                 customer_id: Optional[str] = None, tags: Optional[object] = None,
                 status: Optional[List[PaymentStatus]] = None, type: Optional[List[PaymentTypes]] = None,
                 direction: Optional[List[PaymentDirections]] = None, since: Optional[str] = None,
                 until: Optional[str] = None, sort: Optional[Literal["createdAt", "-createdAt"]] = None,
                 include: Optional[str] = None):
        self.limit = limit
        self.offset = offset
        self.account_id = account_id
        self.customer_id = customer_id
        self.tags = tags
        self.status = status
        self.type = type
        self.direction = direction
        self.since = since
        self.until = until
        self.sort = sort
        self.include = include

    def to_dict(self) -> Dict:
        parameters = {"page[limit]": self.limit, "page[offset]": self.offset}
        if self.customer_id:
            parameters["filter[customerId]"] = self.customer_id
        if self.account_id:
            parameters["filter[accountId]"] = self.account_id
        if self.tags:
            parameters["filter[tags]"] = self.tags
        if self.status:
            for idx, status_filter in enumerate(self.status):
                parameters[f"filter[status][{idx}]"] = status_filter
        if self.type:
            for idx, type_filter in enumerate(self.type):
                parameters[f"filter[type][{idx}]"] = type_filter
        if self.direction:
            for idx, direction_filter in enumerate(self.direction):
                parameters[f"filter[direction][{idx}]"] = direction_filter
        if self.since:
            parameters["filter[since]"] = self.since
        if self.until:
            parameters["filter[until]"] = self.until
        if self.sort:
            parameters["sort"] = self.sort
        if self.include:
            parameters["include"] = self.include
        return parameters

class ListReceivedPaymentParams(UnitParams):
    def __init__(self, limit: int = 100, offset: int = 0, account_id: Optional[str] = None,
                 customer_id: Optional[str] = None, tags: Optional[object] = None,
                 status: Optional[List[AchReceivedPaymentStatus]] = None,
                 direction: Optional[List[PaymentDirections]] = None, include_completed: Optional[bool] = None,
                 sort: Optional[Literal["createdAt", "-createdAt"]] = None, include: Optional[str] = None):
        self.limit = limit
        self.offset = offset
        self.account_id = account_id
        self.customer_id = customer_id
        self.tags = tags
        self.status = status
        self.include_completed = include_completed
        self.sort = sort
        self.include = include

    def to_dict(self) -> Dict:
        parameters = {"page[limit]": self.limit, "page[offset]": self.offset}
        if self.customer_id:
            parameters["filter[customerId]"] = self.customer_id
        if self.account_id:
            parameters["filter[accountId]"] = self.account_id
        if self.tags:
            parameters["filter[tags]"] = self.tags
        if self.include_completed:
            parameters["filter[includeCompleted]"] = self.include_completed
        if self.status:
            for idx, status_filter in enumerate(self.status):
                parameters[f"filter[status][{idx}]"] = status_filter
        if self.sort:
            parameters["sort"] = self.sort
        if self.include:
            parameters["include"] = self.include
        return parameters


class ListRecurringPaymentParams(UnitParams):
    def __init__(self, limit: int = 100, offset: int = 0, account_id: Optional[str] = None,
                 customer_id: Optional[str] = None, tags: Optional[object] = None,
                 status: Optional[List[AchReceivedPaymentStatus]] = None,
                 _type: Optional[List[str]] = None, from_start_time: Optional[str] = None,
                 to_start_time: Optional[str] = None,  from_end_time: Optional[str] = None,
                 to_end_time: Optional[str] = None, sort: Optional[Literal["createdAt", "-createdAt"]] = None):
        self.limit = limit
        self.offset = offset
        self.account_id = account_id
        self.customer_id = customer_id
        self.tags = tags
        self.status = status
        self._type = _type
        self.from_start_time = from_start_time
        self.to_start_time = to_start_time
        self.from_end_time = from_end_time
        self.to_end_time = to_end_time
        self.sort = sort

    def to_dict(self) -> Dict:
        parameters = {"page[limit]": self.limit, "page[offset]": self.offset}
        if self.customer_id:
            parameters["filter[customerId]"] = self.customer_id
        if self.account_id:
            parameters["filter[accountId]"] = self.account_id
        if self.tags:
            parameters["filter[tags]"] = self.tags
        if self.status:
            for idx, status_filter in enumerate(self.status):
                parameters[f"filter[status][{idx}]"] = status_filter
        if self._type:
            for idx, type_filter in enumerate(self._type):
                parameters[f"filter[type][{idx}]"] = type_filter
        if self.from_start_time:
            parameters["filter[fromStartTime]"] = self.from_start_time
        if self.to_start_time:
            parameters["filter[toStartTime]"] = self.to_start_time
        if self.from_end_time:
            parameters["filter[fromEndTime]"] = self.from_end_time
        if self.to_end_time:
            parameters["filter[toEndTime]"] = self.to_end_time
        if self.sort:
            parameters["sort"] = self.sort
        return parameters
