from unit.api.base_resource import BaseResource
from unit.models.counterparty import *
from unit.models.codecs import DtoDecoder


class CounterpartyResource(BaseResource):
    def __init__(self, api_url, token):
        super().__init__(api_url, token)
        self.resource = "counterparties"

    def create(self, request: Union[CreateCounterpartyRequest, CreateCounterpartyWithTokenRequest]) -> Union[UnitResponse[CounterpartyDTO], UnitError]:
        payload = request.to_json_api()
        response = super().post(self.resource, payload)
        if super().is_20x(response.status_code):
            data = response.json().get("data")
            return UnitResponse[CounterpartyDTO](DtoDecoder.decode(data), None)
        else:
            return UnitError.from_json_api(response.json())

    def update(self, request: PatchCounterpartyRequest) -> Union[UnitResponse[CounterpartyDTO], UnitError]:
        payload = request.to_json_api()
        response = super().patch(f"{self.resource}/{request.counterparty_id}", payload)
        if super().is_20x(response.status_code):
            data = response.json().get("data")
            return UnitResponse[CounterpartyDTO](DtoDecoder.decode(data), None)
        else:
            return UnitError.from_json_api(response.json())

    def delete(self, counterparty_id: str) -> Union[UnitResponse, UnitError]:
        response = super().delete(f"{self.resource}/{counterparty_id}")
        if super().is_20x(response.status_code):
            return UnitResponse([], None)
        else:
            return UnitError.from_json_api(response.json())

    def get(self, counterparty_id: str) -> Union[UnitResponse[CounterpartyDTO], UnitError]:
        response = super().get(f"{self.resource}/{counterparty_id}")
        if super().is_20x(response.status_code):
            data = response.json().get("data")
            return UnitResponse[CounterpartyDTO](DtoDecoder.decode(data), None)
        else:
            return UnitError.from_json_api(response.json())

    def list(self, offset: int = 0, limit: int = 100) -> Union[UnitResponse[list[CounterpartyDTO]], UnitError]:
        response = super().get(self.resource, {"page[limit]": limit, "page[offset]": offset})
        if super().is_20x(response.status_code):
            data = response.json().get("data")
            return UnitResponse[CounterpartyDTO](DtoDecoder.decode(data), None)
        else:
            return UnitError.from_json_api(response.json())