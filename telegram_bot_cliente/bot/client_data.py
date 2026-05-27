from pydantic import BaseModel, Field
from typing import Optional, List

class PersonalInfo(BaseModel):
    name_katakana: str = Field(..., min_length=1)
    name_full: str = Field(..., min_length=1)
    birthdate: str
    address: str
    cep: str
    email: str
    phone: str
    nationality: str

class EmploymentInfo(BaseModel):
    company_name: str
    company_address: str
    company_cep: str
    work_location: str
    work_address: str
    work_cep: str
    annual_income: int
    contract_type: str
    hire_date: str
    payment_date: int

class FamilyInfo(BaseModel):
    marital_status: str
    dependents: List[dict] = Field(default_factory=list)

class FinancingInfo(BaseModel):
    liquidated_last_3m: bool
    liquidated_details: Optional[str] = None
    active_financings: List[dict] = Field(default_factory=list)

class SpecialInfo(BaseModel):
    has_side_job: bool
    is_maternity_leave: bool
    has_existing_illness: bool
    illness_name: Optional[str] = None
    takes_medication: bool
    medication_details: Optional[str] = None
    additional_notes: Optional[str] = None

class ClientData(BaseModel):
    personal: Optional[PersonalInfo] = None
    employment: Optional[EmploymentInfo] = None
    family: Optional[FamilyInfo] = None
    financing: Optional[FinancingInfo] = None
    special: Optional[SpecialInfo] = None

    def is_complete(self) -> bool:
        return all([self.personal, self.employment, self.family, self.financing, self.special])
