import typing
import pydantic


ModelType = typing.TypeVar('ModelType')


class Schema(pydantic.BaseModel):
    class Config:
        validate_all = True
        validate_assignment = True
        orm_mode = True


SchemaType = typing.TypeVar('SchemaType')
