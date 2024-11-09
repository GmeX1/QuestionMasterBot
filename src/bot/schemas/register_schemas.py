from pydantic import BaseModel, Field
from typing import Optional, Literal


class RegProfile(BaseModel):
    tg_id: Optional[int] = Field(default=None)
    full_name: Optional[str] = Field(pattern="^['-еЁа-яА-Яa-zA-Z]+ ['-еЁа-яА-Яa-zA-Z]+ ['-еЁа-яА-Яa-zA-Z]+$", default=None)
    # На случай, если кто-то является иностранцем и регается на иностранный номер.
    phone_number: Optional[str] = Field(pattern='^[+]?\\d{11,15}$', default=None)
    client_type: Optional[Literal['Организация', 'Частное лицо', 'Собственник']] = Field(default=None)
    organization_name: Optional['str'] = Field(default=None)
